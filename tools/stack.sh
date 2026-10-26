#!/usr/bin/env bash
# Install selected Codex content from a trusted local snapshot. Linux, Bash 4.4+.
set -Eeuo pipefail
export LC_ALL=C

# Keep terminal presentation independent of the installation plan and log output.
interactive=0 verbose=0
ui_reset='' ui_bold='' ui_muted='' ui_accent='' ui_green='' ui_yellow='' ui_red=''
if [[ -t 1 && -t 2 && ${TERM:-dumb} != dumb && ! ${NO_COLOR+x} ]]; then
    ui_reset=$'\033[0m' ui_bold=$'\033[1m' ui_muted=$'\033[2m'
    ui_accent=$'\033[36m' ui_green=$'\033[32m' ui_yellow=$'\033[33m' ui_red=$'\033[31m'
fi
ui_width=${COLUMNS:-72}
if [[ ! ${COLUMNS:-} && -t 2 ]] && command -v stty >/dev/null; then
    read -r _ ui_width < <(stty size <&2 2>/dev/null) || ui_width=72
fi
[[ $ui_width =~ ^[1-9][0-9]{0,2}$ ]] || ui_width=72
(( ui_width <= 72 )) || ui_width=72
(( ui_width >= 20 )) || ui_width=20
ui_line() {
    local text=$1 style=${2:-} width=$((ui_width-4)) part
    while (( ${#text} > width )); do
        part=${text:0:width}
        [[ $part != *' '* ]] || part=${part% *}
        [[ -n $part ]] || part=${text:0:width}
        printf '  %s%s%s\n' "$style" "$part" "$ui_reset" >&2
        text=${text:${#part}}; text=${text# }
    done
    printf '  %s%s%s\n' "$style" "$text" "$ui_reset" >&2
}
ui_rule() {
    local line; printf -v line '%*s' "$((ui_width-4))" ''
    ui_line "${line// /-}" "$ui_muted"
}
ui_heading() { printf '\n' >&2; ui_line "$1" "$ui_bold"; ui_rule; }
ui_notice() {
    local style=$ui_accent
    case $1 in success) style=$ui_green ;; warning) style=$ui_yellow ;; error) style=$ui_red ;; esac
    if (( interactive )); then ui_line "$2" "$style"
    else printf '%s%s%s\n' "$style" "$2" "$ui_reset" >&2; fi
}
ui_option() { ui_line "[$1] $2" "$ui_accent$ui_bold"; ui_line "    $3" "$ui_muted"; printf '\n' >&2; }
ui_field() { ui_line "$1" "$ui_muted"; ui_line "  $2"; }
ui_brand() {
    printf '\n' >&2
    ui_line '===  AI Engineering Stack' "$ui_accent$ui_bold"
    ui_line '=====  Your tools. Your project.' "$ui_muted"
    ui_rule
    ui_line "Installer $version  /  Bash + jq" "$ui_muted"
}
profile_label() {
    case $1 in
        core) REPLY=Core ;; nestjs) REPLY=NestJS ;; react) REPLY=React ;;
        nextjs) REPLY=Next.js ;; spring-boot) REPLY='Spring Boot' ;; *) REPLY=$1 ;;
    esac
}
profile_summary() {
    case $1 in
        core) REPLY='Shared workflow, diagnosis and local project records.' ;;
        nestjs) REPLY='Backend conventions and focused NestJS guidance.' ;;
        react) REPLY='Components, rendering and React performance guidance.' ;;
        nextjs) REPLY='Next.js context with shared React guidance.' ;;
        spring-boot) REPLY='Java, Maven and Spring Boot project context.' ;;
        *) REPLY=$(jq -r '.description' "$SOURCE/profiles/$1.json") ;;
    esac
}
fail() { ui_notice error "Stack operation failed: $*"; exit 1; }
(( BASH_VERSINFO[0] > 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] >= 4) )) || fail 'Bash 4.4+ is required'
for dependency in jq realpath sha256sum base64 mktemp cp mv chmod mkdir rm find sort cmp awk cat dirname; do
    command -v "$dependency" >/dev/null || fail "Required command is missing: $dependency"
done
SOURCE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
WORK=$(mktemp -d "${TMPDIR:-/tmp}/ai-stack.XXXXXXXX")
transaction=0
recover=1
declare -a keys=() applied=()
declare -A paths=() kinds=() desired=() retired=() old_hash=()

# Inspect the lexical path before normalization so a symlink followed by /.. is rejected.
safe_path() {
    local raw=$1 check
    [[ $raw != '~' ]] || raw=$HOME
    [[ $raw != '~/'* ]] || raw=$HOME/${raw:2}
    [[ $raw == /* ]] || raw=$PWD/$raw
    [[ $raw != *$'\n'* && $raw != *$'\r'* && $raw != *$'\t'* ]] || fail 'Paths cannot contain tabs or newlines'
    check=${raw%/}
    while [[ -n $check ]]; do
        [[ ! -L $check ]] || fail "Symlink not allowed: $check"
        [[ $check == "${raw%/}" || ! -e $check || -d $check ]] || fail "Parent is not a directory: $check"
        check=${check%/*}
    done
    REPLY=$(realpath -ms -- "$raw")
}
check_file() {
    safe_path "$1"
    [[ ! -e $1 || -f $1 ]] || fail "Expected a regular file: $1"
}
encode() {
    if [[ -e $1 ]]; then base64 -w 0 -- "$1"; else printf '~'; fi
}
decode() {
    if [[ $1 != '~' ]]; then printf '%s' "$1" | base64 -d > "$2"; fi
}
hash_file() { local result; result=$(sha256sum -- "$1"); REPLY=${result%% *}; }
same() { [[ ! -e $1 && ! -e $2 ]] || { [[ -f $1 && -f $2 ]] && cmp -s -- "$1" "$2"; }; }
atomic_write() {
    local path=$1 data=$2 executable=${3:-0} temporary
    check_file "$path"
    if [[ ! -e $data ]]; then rm -f -- "$path"; return; fi
    mkdir -p -- "${path%/*}"
    temporary=$(mktemp "${path%/*}/.ai-stack-XXXXXXXX")
    if ! { cp -- "$data" "$temporary" &&
        { if [[ -e $path ]]; then chmod --reference="$path" "$temporary"; else chmod 600 "$temporary"; fi; } &&
        { if (( executable )); then chmod u+x "$temporary"; fi; } && mv -f -- "$temporary" "$path"; }; then
        rm -f -- "$temporary"
        return 1
    fi
}
finish() {
    local code=$? index
    trap - EXIT ERR INT TERM
    if (( code != 0 && transaction && recover )); then
        set +e
        printf 'Restoring files after a failed write.\n' >&2
        local restored=1
        for ((index=${#applied[@]}-1; index>=0; index--)); do
            atomic_write "${paths[${applied[index]}]}" "$WORK/before-${applied[index]}" || restored=0
        done
        atomic_write "$state_path" "$WORK/previous-state" || restored=0
        if (( restored )); then
            atomic_write "$backup_path" "$WORK/previous-backup" || restored=0
        fi
        (( restored )) || printf 'Recovery incomplete; preserve backup.json and run rollback before retrying.\n' >&2
    fi
    rm -rf -- "$WORK"
    exit "$code"
}
trap finish EXIT
trap 'printf "Stack operation failed near line %s.\n" "$LINENO" >&2; exit 1' ERR
trap 'recover=0; printf "Interrupted; run rollback before retrying.\n" >&2; exit 130' INT TERM

usage() {
    cat <<'USAGE'
Usage: bash tools/stack.sh [menu | install | init TARGET | status [TARGET] | rollback [TARGET]] [OPTIONS]

No command opens the interactive installer. Choose global installation or a project profile.
The project menu confirms the current working directory before profile selection.
Project profiles are read from stack.json and profiles/*.json.

  --profile NAME      Project profile (init/status/rollback); default: recorded profile or core
  --global            Global status or rollback (install is already global)
  --prefix PATH       Global package (default: ~/.local/share/ai-engineering-stack)
  --bin-dir PATH      Launcher directory (default: ~/.local/bin)
  --codex-home PATH   Codex configuration (default: $CODEX_HOME or ~/.codex)
  --skills-dir PATH   Global skills destination (default: ~/.agents/skills)
  --dry-run           Preview only; do not write installation destinations
  --verbose           Show every changed file in the interactive preview
  -h, --help          Show this help

Requirements: Bash 4.4+, jq 1.6+, GNU coreutils, find, sort, and awk. No Python runtime.
USAGE
}
command=menu target='' profile='' global_scope=0 dry_run=0
prefix='~/.local/share/ai-engineering-stack' bin_dir='~/.local/bin'
codex_home=${CODEX_HOME:-'~/.codex'} skills_dir=''
if (( $# )) && [[ $1 != -* ]]; then command=$1; shift; fi
case $command in menu|install|init|status|rollback) ;; *) fail "Unknown command: $command" ;; esac
while (( $# )); do
    case $1 in
        --prefix|--bin-dir|--codex-home|--skills-dir|--profile)
            (( $# >= 2 )) && [[ -n $2 ]] || fail "Missing value for $1"
            case $1 in
                --prefix) prefix=$2 ;; --bin-dir) bin_dir=$2 ;; --codex-home) codex_home=$2 ;;
                --skills-dir) skills_dir=$2 ;; --profile) profile=$2 ;;
            esac
            shift 2 ;;
        --global) global_scope=1; shift ;; --dry-run) dry_run=1; shift ;;
        --verbose) verbose=1; shift ;;
        -h|--help) usage; exit 0 ;; --*) fail "Unknown option: $1" ;;
        *) [[ -z $target && $command != install ]] || fail 'Unexpected project target'; target=$1; shift ;;
    esac
done
[[ $command != init || $global_scope == 0 ]] || fail 'Use install for global installation'
[[ $global_scope == 0 || -z $target ]] || fail 'Do not combine --global with a project target'
[[ $command != install || -z $profile ]] || fail 'Profiles belong to project initialization'

manifest=$SOURCE/stack.json
jq -e 'type == "object" and (.version | type == "string")
    and all(.installationFiles, .profiles, .nativeAgents, .projectAgents, .globalSkills, .skills;
        type == "array" and all(.[]; type == "string"))
    and all(.profiles[]; test("^profiles/[a-z0-9-]+\\.json$"))
    and (.mcpConfiguration | type == "string")' "$manifest" >/dev/null || fail 'Invalid installation manifest'
version=$(jq -r '.version' "$manifest")
jq -r '.profiles[] | capture("^profiles/(?<id>[a-z0-9-]+)\\.json$").id' "$manifest" > "$WORK/profiles"
mapfile -t profiles < "$WORK/profiles"
(( ${#profiles[@]} )) || fail 'No profiles are available'
valid_profile() { local name; for name in "${profiles[@]}"; do [[ $name != "$1" ]] || return 0; done; return 1; }
prompt() {
    ui_line "$1" "$ui_bold"
    printf '  %s>%s ' "$ui_accent" "$ui_reset" >&2
    IFS= read -r REPLY || fail 'Input ended; no selection was applied'
}
if [[ $command == menu ]]; then
    [[ -t 0 ]] || fail 'Interactive installation needs a terminal; use install or init TARGET --profile NAME'
    [[ -z $target && -z $profile && $global_scope == 0 ]] || fail 'Use explicit commands with target/profile/global options'
    interactive=1
    ui_brand
    ui_heading 'Choose where to install'
    ui_option 1 'Global catalog' 'Install or update shared tools for your Codex environment.'
    ui_option 2 'Project profile' 'Add the selected framework guidance to an existing project.'
    ui_option 0 Exit 'Leave without making changes.'
    (( dry_run == 0 )) || ui_notice warning 'Preview mode: installation destinations stay unchanged.'
    while :; do
        prompt 'Select an action [0-2]'
        case $REPLY in 0) ui_notice success 'See you next time.'; exit 0 ;; 1) command=install; break ;; 2) command=init; break ;; *) ui_notice warning 'Choose 0, 1 or 2.' ;; esac
    done
    if [[ $command == init ]]; then
        # The caller's working directory is independent of the script's location.
        safe_path "$PWD"; target=$REPLY
        ui_heading 'Confirm your project'
        ui_line 'The profile will be installed where you started the installer.' "$ui_muted"
        ui_field 'Project directory' "$target"
        prompt 'Is this the correct directory? [y/N]'
        [[ $REPLY == y || $REPLY == Y || $REPLY == yes ]] || {
            ui_notice warning 'Cancelled; no installation destinations changed.'
            ui_line 'Run the installer from the intended project directory.' "$ui_muted"
            exit 0
        }
        ui_heading 'Choose a profile'
        ui_line 'Every profile includes the shared core. Select one:' "$ui_muted"
        printf '\n' >&2
        for index in "${!profiles[@]}"; do
            profile_label "${profiles[index]}"; label=$REPLY
            profile_summary "${profiles[index]}"
            ui_option "$((index+1))" "$label" "$REPLY"
        done
        ui_option 0 Cancel 'Leave without making changes.'
        while :; do
            prompt "Select a profile [1-${#profiles[@]}]"
            [[ $REPLY != 0 ]] || { ui_notice warning 'Cancelled; no installation destinations changed.'; exit 0; }
            if [[ $REPLY =~ ^[1-9][0-9]?$ ]] && (( REPLY <= ${#profiles[@]} )); then profile=${profiles[REPLY-1]}; break; fi
            ui_notice warning 'Choose a listed profile number.'
        done
    fi
else interactive=0; fi
[[ -z $profile ]] || valid_profile "$profile" || fail "Unknown profile: $profile"

add_file() {
    local key=$1 path=$2 kind=$3 data=$4
    [[ ! ${paths[$key]+present} ]] || fail "Duplicate managed path: $key"
    check_file "$path"
    paths[$key]=$path kinds[$key]=$kind desired[$key]=$data keys+=("$key")
}
relative_path() {
    [[ $1 =~ ^[a-zA-Z0-9_./-]+$ && $1 != /* && $1 != */ && $1 != *//* && /$1/ != */../* && /$1/ != */./* ]] || fail "Invalid package path: $1"
}
source_file() { relative_path "$1"; check_file "$SOURCE/$1"; [[ -f $SOURCE/$1 ]] || fail "Missing package source: $1"; }
add_skills() {
    local name=$1 root=$2 destination=$3 key_prefix=$4 file relative
    [[ $name =~ ^[a-z0-9-]+$ ]] || fail "Invalid skill name: $name"
    source_file "skills/$name/SKILL.md"
    find "$SOURCE/skills/$name" -print0 | sort -z > "$WORK/skill-paths"
    while IFS= read -r -d '' file; do
        [[ ! -L $file ]] || fail "Symlink skill source: $file"
        [[ -f $file ]] || continue
        relative=$name/${file#"$SOURCE/skills/$name/"}
        relative_path "$relative"
        add_file "$key_prefix$destination$relative" "$root/$destination$relative" file "$file"
    done < "$WORK/skill-paths"
}
make_block() {
    jq -jRs '"<!-- BEGIN:ai-engineering-stack -->\n" + sub("\\s+$"; "") + "\n<!-- END:ai-engineering-stack -->"' "$1" > "$2"
}
extract_block() {
    local input=$1 output=$2
    if [[ ! -e $input ]]; then rm -f -- "$output"; return; fi
    # Refuse non-UTF-8 instruction text rather than changing bytes outside the block.
    jq -jRs '.' "$input" > "$WORK/roundtrip"
    cmp -s -- "$input" "$WORK/roundtrip" || fail "Instructions must be valid UTF-8: $input"
    jq -L "$SOURCE/tools" -jRs 'include "installer"; managed | if . == null then empty else .string end' "$input" > "$output"
    [[ -s $output ]] || rm -f -- "$output"
}
replace_block() {
    local input=$1 replacement=$2 output=$3
    [[ -e $input ]] || input=$WORK/empty
    [[ -e $replacement ]] || replacement=$WORK/empty
    jq -L "$SOURCE/tools" -jn --rawfile text "$input" --rawfile replacement "$replacement" \
        'include "installer"; $text | replace_managed(if $replacement == "" then null else $replacement end)' > "$output"
}
: > "$WORK/empty"
safe_path "$codex_home"; codex_home=$REPLY
check_file "$codex_home/AGENTS.override.md"
[[ ! -s $codex_home/AGENTS.override.md ]] || fail 'Non-empty global AGENTS.override.md would hide stack guidance'
if [[ $command == install || $global_scope == 1 ]]; then
    scope=global profile=core
    safe_path "$prefix"; prefix=$REPLY
    safe_path "$bin_dir"; bin_dir=$REPLY
    safe_path "${CODEX_HOME:-'~/.codex'}"; default_codex=$REPLY
    if [[ -z $skills_dir ]]; then
        if [[ $codex_home == "$default_codex" ]]; then skills_dir=$HOME/.agents/skills; else skills_dir=${codex_home%/*}/.agents/skills; fi
    fi
    safe_path "$skills_dir"; skills_dir=$REPLY
    roots=$(jq -cn --arg package "$prefix" --arg bin "$bin_dir" --arg codex "$codex_home" --arg skills "$skills_dir" '{package:$package,bin:$bin,codex:$codex,skills:$skills}')
    root_values=("$prefix" "$bin_dir" "$codex_home" "$skills_dir")
    for index in "${!root_values[@]}"; do
        root=${root_values[index]}
        if [[ $index == 0 && $root == "$SOURCE" && -f $root/installation.json ]]; then :
        else
            [[ $root != / && $root != "$HOME" && $root != "$SOURCE" && $root != "$SOURCE/"* && $SOURCE != "$root/"* ]] || fail 'Global destinations must be outside the stack source and home/filesystem roots'
        fi
        for other in "${!root_values[@]}"; do
            [[ $index == "$other" ]] && continue
            [[ $root != "${root_values[other]}" && $root != "${root_values[other]}/"* ]] || fail 'Global destination directories must not overlap'
        done
    done
    state_path=$prefix/installation.json backup_path=$prefix/backup.json
    check_file "$state_path"; check_file "$backup_path"
    [[ ! -e $state_path ]] || jq -e '.files | type == "object"' "$state_path" >/dev/null
    while IFS= read -r relative; do
        relative_path "$relative"
        [[ $relative != installation.json && $relative != backup.json ]] || fail "Invalid package path: $relative"
        source_file "$relative"
        add_file "package/$relative" "$prefix/$relative" file "$SOURCE/$relative"
    done < <(jq -r '.installationFiles[]' "$manifest")
    # Only this retired path is supported, for a reversible Python-to-Bash migration.
    add_file package/tools/stack.py "$prefix/tools/stack.py" file "$WORK/absent"
    retired[package/tools/stack.py]=1
    printf '#!/usr/bin/env bash\nexec bash %q "$@"\n' "$prefix/tools/stack.sh" > "$WORK/launcher"
    add_file bin/ai-stack "$bin_dir/ai-stack" file "$WORK/launcher"
    template=$(jq -r '.globalInstructions' "$SOURCE/adapters/codex/adapter.json"); source_file "$template"
    make_block "$SOURCE/$template" "$WORK/global-block"
    add_file codex/AGENTS.md "$codex_home/AGENTS.md" block "$WORK/global-block"
    while IFS= read -r relative; do
        source_file "$relative"
        add_file "codex/agents/${relative##*/}" "$codex_home/agents/${relative##*/}" file "$SOURCE/$relative"
    done < <(jq -r '.nativeAgents[]' "$manifest")
    : > "$WORK/external.tsv"
    while IFS= read -r name; do
        [[ $name =~ ^[a-z0-9-]+$ ]] || fail "Invalid skill name: $name"
        jq -e --arg name "$name" '.skills | index("skills/" + $name + "/SKILL.md") != null' "$manifest" >/dev/null || fail "Unknown global skill: $name"
        external=$skills_dir/$name/SKILL.md; check_file "$external"
        if [[ -f $external ]] && { [[ ! -e $state_path ]] || ! jq -e --arg key "skills/$name/SKILL.md" '.files | has($key)' "$state_path" >/dev/null; }; then
            awk -v name="$name" '$0 ~ "^name: *[\047\042]?" name "[\047\042]? *\\r?$" {found=1} END {exit !found}' "$external" || fail "Existing global skill has mismatched metadata: $external"
            hash_file "$external"
            printf '%s\t%s\t%s\n' "$name" "$external" "$REPLY" >> "$WORK/external.tsv"
            if (( ! interactive || verbose )); then printf 'Reuse existing global skill (externally managed): %s\n' "$external"; fi
            policy=skills/$name/agents/openai.yaml
            if [[ -f $SOURCE/$policy ]]; then source_file "$policy"; add_file "$policy" "$skills_dir/$name/agents/openai.yaml" file "$SOURCE/$policy"; fi
        else add_skills "$name" "$skills_dir" '' skills/; fi
    done < <(jq -r '.globalSkills[]' "$manifest")
    external_skills=$(jq -Rn '[inputs | split("\t") | {key:.[0],value:{path:.[1],sha256:.[2]}}] | from_entries' < "$WORK/external.tsv")
    relative=$(jq -r '.mcpConfiguration' "$manifest"); source_file "$relative"
    add_file codex/stack-development.config.toml "$codex_home/stack-development.config.toml" file "$SOURCE/$relative"
    if (( ! interactive || verbose )); then printf 'MCP definitions are available through --profile stack-development; authentication and connection checks are separate.\n'; fi
else
    scope=project
    [[ -n $target ]] || fail 'A project target is required unless --global is selected'
    safe_path "$target"; target=$REPLY
    [[ -d $target ]] || fail 'Project must be an existing directory; scaffolding is separate'
    [[ $target != / && $target != "$HOME" && $target != "$SOURCE" && $target != "$SOURCE/"* && $SOURCE != "$target/"* ]] || fail 'Choose a project outside the stack source, home root, and filesystem root'
    [[ /$target/ != */.git/* && /$target/ != */.codex/* && /$target/ != */.agents/* && /$target/ != */.aws/* ]] || fail 'A client or metadata directory cannot be the project root'
    check_file "$target/AGENTS.override.md"
    [[ ! -s $target/AGENTS.override.md ]] || fail 'Non-empty project AGENTS.override.md would hide stack guidance'
    check_file "$codex_home/AGENTS.md"
    if [[ $command == init ]]; then
        extract_block "$codex_home/AGENTS.md" "$WORK/global-block"
        [[ -s $WORK/global-block ]] || fail 'Install global core first, using the same Codex home'
    fi
    roots=$(jq -cn --arg project "$target" '{project:$project}')
    state_path=$target/.ai-stack/installation.json backup_path=$target/.ai-stack/backup.json
    check_file "$state_path"; check_file "$backup_path"
    recorded=core
    if [[ -e $state_path ]]; then recorded=$(jq -er '.selection.profile | strings' "$state_path"); fi
    if [[ $command == rollback && -f $backup_path && -z $profile ]]; then
        # A first init or core-to-framework promotion can stop before state commits.
        profile=$(jq -er '.afterState | @base64d | fromjson | .selection.profile | strings' "$backup_path")
    fi
    profile=${profile:-$recorded}
    valid_profile "$profile" || fail "Unknown profile: $profile"
    [[ ! -e $state_path || $profile == "$recorded" || $recorded == core ]] || fail 'Changing an initialized profile requires rollback first; existing files were preserved'
    # Resolve inheritance from the JSON catalog, rejecting cycles and unknown parents.
    : > "$WORK/profile-order"
    resolve_profile() {
        local id=$1 active=$2 parent
        valid_profile "$id" || fail "Unknown profile: $id"
        [[ $active != *"|$id|"* ]] || fail 'Cyclic profile inheritance'
        source_file "profiles/$id.json"
        jq -e --arg id "$id" '.id == $id and (.description | type == "string") and (.skills | type == "array") and (.extends | type == "array")' "$SOURCE/profiles/$id.json" >/dev/null
        local parents; parents=$(jq -r '.extends[]' "$SOURCE/profiles/$id.json")
        while IFS= read -r parent; do [[ -z $parent ]] || resolve_profile "$parent" "$active|$id|"; done <<< "$parents"
        printf '%s\n' "$id" >> "$WORK/profile-order"
    }
    resolve_profile "$profile" ''
    mapfile -t ordered < <(awk '!seen[$0]++' "$WORK/profile-order")
    profile_files=(); for name in "${ordered[@]}"; do profile_files+=("$SOURCE/profiles/$name.json"); done
    jq -sr '[.[].skills[]] | unique[]' "${profile_files[@]}" > "$WORK/selected-skills"
    template=$(jq -r '.projectInstructions' "$SOURCE/adapters/codex/adapter.json"); source_file "$template"
    jq -jRs 'sub("\\s+$"; "")' "$SOURCE/$template" > "$WORK/context"
    printf '\n\nSelected profile: `%s`.\n' "$profile" >> "$WORK/context"
    jq -r '.description' "${profile_files[@]}" >> "$WORK/context"
    if [[ $profile == spring-boot ]]; then
        check_file "$target/pom.xml"
        if [[ -f $target/pom.xml ]]; then
            # Observe literal Maven declarations, without executing Maven or resolving XML entities.
            awk 'BEGIN {RS="<"; FS=">"; boot=java=release=parent=version="not declared"}
                {tag=$1; text=$2; gsub(/^[[:space:]]+|[[:space:]]+$/, "", text);
                 if (tag ~ /^[!?]/ || tag == "") next;
                 closing=(tag ~ /^\//); sub(/^\//,"",tag); sub(/[[:space:]].*$/,"",tag); sub(/^.*:/,"",tag);
                 if (closing) {if (depth>0) depth--; next} node[++depth]=tag;
                 path=""; for(i=1;i<=depth;i++) path=path "/" node[i];
                 if(path=="/project/parent/artifactId") parent=text;
                 if(path=="/project/parent/version") version=text;
                 if(path=="/project/properties/spring-boot.version") boot=text;
                 if(path=="/project/properties/java.version") java=text;
                 if(path=="/project/properties/maven.compiler.release") release=text;
                 if ($1 ~ /\/$/) depth--;
                }
                END {if(parent=="spring-boot-starter-parent") boot=version; if(java=="not declared") java=release;
                     printf "Declared Spring Boot: %s; Java: %s. Use Maven; inspect resolved versions before coding.\n",boot,java}' "$target/pom.xml" >> "$WORK/context"
        else printf 'No pom.xml detected. Inspect Java and Spring Boot versions before coding.\n' >> "$WORK/context"; fi
    elif [[ $profile != core && -e $target/package.json ]]; then
        check_file "$target/package.json"
        jq -er --arg profile "$profile" '
          if type != "object" or ((.dependencies // {}) | type != "object") or ((.devDependencies // {}) | type != "object")
          then error("package.json must contain an object with dependency maps") else . end
          | ((.devDependencies // {}) + (.dependencies // {})) as $deps
          | (if $profile == "nestjs" then ["@nestjs/core"] elif $profile == "nextjs" then ["react","next"] else ["react"] end)
          | "Declared dependency ranges: " + (map(. + "=" + ($deps[.] // "not declared" | tostring | gsub("[\\r\\n]"; " "))) | join("; "))
            + ". Inspect installed versions; do not upgrade automatically."' "$target/package.json" >> "$WORK/context"
    else printf 'Inspect installed framework versions and existing check commands before coding.\n' >> "$WORK/context"; fi
    printf 'Selected skills: %s.' "$(awk 'BEGIN {sep=""} {printf "%s%s",sep,$0; sep=", "}' "$WORK/selected-skills")" >> "$WORK/context"
    make_block "$WORK/context" "$WORK/project-block"
    add_file AGENTS.md "$target/AGENTS.md" block "$WORK/project-block"
    for name in decisions tasks findings; do
        template=templates/$name.md; source_file "$template"
        add_file ".ai-stack/$name.md" "$target/.ai-stack/$name.md" seed "$SOURCE/$template"
    done
    while IFS= read -r relative; do
        source_file "$relative"
        add_file ".codex/agents/${relative##*/}" "$target/.codex/agents/${relative##*/}" file "$SOURCE/$relative"
    done < <(jq -r '.projectAgents[]' "$manifest")
    while IFS= read -r name; do add_skills "$name" "$target" .agents/skills/ ''; done < "$WORK/selected-skills"
    external_skills='{}'
fi

# Validate every path and state before writing any installation destination.
: > "$WORK/kinds.tsv"
for key in "${keys[@]}"; do printf '%s\t%s\n' "$key" "${kinds[$key]}" >> "$WORK/kinds.tsv"; done
jq -Rn '[inputs | split("\t") | {key:.[0],value:.[1]}] | from_entries' < "$WORK/kinds.tsv" > "$WORK/kinds.json"
profiles_json=$(jq -Rn '[inputs]' < "$WORK/profiles")
validate_state() {
    jq -L "$SOURCE/tools" -e --argjson roots "$roots" --arg scope "$scope" --slurpfile kinds "$WORK/kinds.json" --argjson profiles "$profiles_json" \
        'include "installer"; valid_state($roots; $scope; $kinds[0]; $profiles)' "$1" >/dev/null || fail 'Installation state does not match this scope, location, or schema'
}
if [[ -f $state_path ]]; then
    cp -- "$state_path" "$WORK/previous-state"
    validate_state "$state_path"
    while IFS=$'\t' read -r key hash; do old_hash[$key]=$hash; done < <(jq -r '.files | to_entries[] | [.key,.value.sha256] | @tsv' "$state_path")
fi
if [[ -f $backup_path ]]; then cp -- "$backup_path" "$WORK/previous-backup"; fi
validate_backup() {
    jq -L "$SOURCE/tools" -e --argjson roots "$roots" --arg scope "$scope" \
        'include "installer"; type == "object" and .schemaVersion == 1 and .scope == $scope
        and (.roots | roots_match($roots; $scope)) and (.changes | type == "array")
        and (.afterState | type == "string") and (.previousState | . == null or type == "string")' "$backup_path" >/dev/null || fail 'Backup does not belong to this installation'
    local value
    value=$(jq -r '.afterState' "$backup_path"); decode "$value" "$WORK/backup-after-state"; validate_state "$WORK/backup-after-state"
    value=$(jq -r '.previousState // "~"' "$backup_path"); decode "$value" "$WORK/backup-before-state"
    [[ ! -e $WORK/backup-before-state ]] || validate_state "$WORK/backup-before-state"
}

if [[ $command == rollback ]]; then
    [[ -f $backup_path ]] || fail 'No installation backup is available'
    validate_backup
    same "$state_path" "$WORK/backup-after-state" || same "$state_path" "$WORK/backup-before-state" || fail 'Installation state changed after the backup; rollback refused'
    jq -e --slurpfile kinds "$WORK/kinds.json" '
        (.changes | map(.key) | length) == (.changes | map(.key) | unique | length)
        and all(.changes[]; .key as $key | ($kinds[0][$key] != null and $kinds[0][$key] != "seed")
            and (.before | . == null or type == "string") and (.after | . == null or type == "string"))' "$backup_path" >/dev/null || fail 'Invalid backup change list'
    changes=()
    index=0
    while IFS=$'\t' read -r key before after; do
        path=${paths[$key]}; check_file "$path"
        decode "$before" "$WORK/rollback-before-$index"; decode "$after" "$WORK/rollback-after-$index"
        # Use numeric temporary IDs; managed keys contain directory separators.
        id=$index; paths[$id]=$path kinds[$id]=${kinds[$key]}
        [[ ! -e $path ]] || cp -- "$path" "$WORK/before-$id"
        if same "$path" "$WORK/rollback-before-$index"; then ((index+=1)); continue; fi
        if [[ ${kinds[$key]} == block ]]; then
            extract_block "$path" "$WORK/current-block"
            extract_block "$WORK/rollback-before-$index" "$WORK/before-block"
            extract_block "$WORK/rollback-after-$index" "$WORK/after-block"
            if same "$WORK/current-block" "$WORK/before-block"; then ((index+=1)); continue; fi
            same "$WORK/current-block" "$WORK/after-block" || fail "Managed instructions changed; preserved: $path"
            if same "$path" "$WORK/rollback-after-$index"; then desired[$id]=$WORK/rollback-before-$index
            else replace_block "$path" "$WORK/before-block" "$WORK/restore-$id"; desired[$id]=$WORK/restore-$id; fi
        else
            same "$path" "$WORK/rollback-after-$index" || fail "File changed after installation; preserved: $path"
            desired[$id]=$WORK/rollback-before-$index
        fi
        changes+=("$id"); ((index+=1))
    done < <(jq -r '.changes[] | [.key,(.before // "~"),(.after // "~")] | @tsv' "$backup_path")
    printf '%s: %s content file(s) and installation state\n' "$(if ((dry_run)); then printf 'Would restore'; else printf Restore; fi)" "${#changes[@]}"
    (( dry_run == 0 )) || exit 0
    transaction=1
    for id in "${changes[@]}"; do
        same "${paths[$id]}" "$WORK/before-$id" || fail "File changed during rollback: ${paths[$id]}"
        applied+=("$id")
        atomic_write "${paths[$id]}" "${desired[$id]}" "$([[ ${paths[$id]} == "$bin_dir/ai-stack" ]] && printf 1 || printf 0)"
    done
    atomic_write "$state_path" "$WORK/backup-before-state"
    atomic_write "$backup_path" "$WORK/absent"
    transaction=0
    printf 'Previous installation restored. Project records were preserved.\n'
    exit 0
fi
if [[ -f $backup_path ]]; then
    validate_backup
    same "$state_path" "$WORK/backup-after-state" || fail 'Existing backup is unowned or records an interrupted operation; preserved'
fi
changes=()
created_count=0 updated_count=0 removed_count=0
: > "$WORK/owned.tsv"; : > "$WORK/changes.tsv"
index=0
for key in "${keys[@]}"; do
    path=${paths[$key]} kind=${kinds[$key]} data=${desired[$key]}
    # Retired paths are removed only when a previous state owns them.
    if [[ ${retired[$key]:-0} == 1 && ! ${old_hash[$key]+present} ]]; then continue; fi
    [[ ! -e $path ]] || cp -- "$path" "$WORK/current-$index"
    if [[ $kind == seed ]]; then
        [[ ! -e $path ]] || { ((index+=1)); continue; }
    else
        unit=$WORK/current-$index
        if [[ $kind == block ]]; then extract_block "$unit" "$WORK/unit-$index"; unit=$WORK/unit-$index; fi
        if [[ ${old_hash[$key]+present} ]]; then
            [[ -f $unit ]] || fail "Managed content changed or missing; preserved: $path"
            hash_file "$unit"
            [[ $REPLY == "${old_hash[$key]}" ]] || fail "Managed content changed or missing; preserved: $path"
        elif [[ -e $unit ]]; then fail "Existing content is not owned by this installation: $path"; fi
        if [[ -e $data ]]; then
            hash_file "$data"; printf '%s\t%s\t%s\n' "$key" "$kind" "$REPLY" >> "$WORK/owned.tsv"
        fi
    fi
    if [[ $kind == block ]]; then replace_block "$WORK/current-$index" "$data" "$WORK/result-$index"; data=$WORK/result-$index; fi
    if ! same "$WORK/current-$index" "$data"; then
        id=$index; paths[$id]=$path kinds[$id]=$kind desired[$id]=$WORK/after-$id
        [[ ! -e $path ]] || cp -- "$path" "$WORK/before-$id"
        [[ ! -e $data ]] || cp -- "$data" "$WORK/after-$id"
        changes+=("$id")
        action=Create; [[ ! -e $path ]] || action=Update; [[ -e $data ]] || action=Remove
        case $action in Create) ((created_count+=1)) ;; Update) ((updated_count+=1)) ;; Remove) ((removed_count+=1)) ;; esac
        if (( ! interactive )); then printf '%s: %s\n' "$action" "$path"
        elif (( verbose )); then ui_line "$action: $path" "$ui_muted"; fi
        if [[ $kind != seed ]]; then printf '%s\t%s\t%s\n' "$key" "$(encode "$WORK/before-$id")" "$(encode "$WORK/after-$id")" >> "$WORK/changes.tsv"; fi
    fi
    ((index+=1))
done
jq -Rn '[inputs | split("\t") | {key:.[0],value:{kind:.[1],sha256:.[2]}}] | from_entries' < "$WORK/owned.tsv" > "$WORK/owned.json"
jq -Sn --arg scope "$scope" --arg version "$version" --argjson roots "$roots" --arg profile "$profile" --argjson external "$external_skills" --slurpfile owned "$WORK/owned.json" \
    '{schemaVersion:1,scope:$scope,version:$version,roots:$roots,selection:({client:"codex",profile:$profile} + (if $scope=="global" then {externalSkills:$external} else {} end)),files:$owned[0]}' > "$WORK/next-state"
state_changed=1
if [[ -e $state_path ]] && jq -e --slurpfile next "$WORK/next-state" '. == $next[0]' "$state_path" >/dev/null; then
    cp -- "$state_path" "$WORK/next-state"; state_changed=0
fi
installed='not installed'; [[ ! -e $state_path ]] || installed=$(jq -r '.version' "$state_path")
preview=$dry_run; [[ $command != status ]] || preview=1
if (( interactive )); then
    ui_heading 'Review installation'
    ui_field Version "$installed -> $version"
    if [[ $scope == global ]]; then
        ui_field Selection 'Global catalog'
        ui_field Package "$prefix"
        ui_field Launcher "$bin_dir/ai-stack"
        ui_field 'Codex home' "$codex_home"
        ui_field 'Shared skills' "$skills_dir"
    else
        profile_label "$profile"; ui_field Profile "$REPLY"
        ui_field Project "$target"
        ui_field Skills "$(awk 'BEGIN {sep=""} {printf "%s%s",sep,$0; sep=", "}' "$WORK/selected-skills")"
    fi
    ui_rule
    ui_line "$created_count new / $updated_count updated / $removed_count removed" "$ui_accent$ui_bold"
    ui_line "${#changes[@]} content file(s), $state_changed state file(s)" "$ui_muted"
    if (( preview )); then
        printf '\n' >&2; ui_notice success 'Preview complete. No installation destinations changed.'; exit 0
    fi
    if (( ${#changes[@]} == 0 && state_changed == 0 )); then
        printf '\n' >&2; ui_notice success 'Everything is up to date.'; exit 0
    fi
    ui_line 'Use --verbose to inspect every planned file path.' "$ui_muted"
    prompt 'Apply this installation? [y/N]'
    [[ $REPLY == y || $REPLY == Y || $REPLY == yes ]] || { ui_notice warning 'Cancelled; no installation destinations changed.'; exit 0; }
    ui_heading 'Installing selected content'
    ui_line 'Writing files and saving the recovery point...' "$ui_muted"
else
    printf 'Scope: %s; installed: %s; available: %s; profile: %s\n' "$scope" "$installed" "$version" "$profile"
    printf '%s: %s content file(s), %s state file(s)\n' "$(if ((preview)); then printf 'Would change'; else printf Planned; fi)" "${#changes[@]}" "$state_changed"
    (( preview == 0 )) || exit 0
    (( ${#changes[@]} || state_changed )) || exit 0
fi
jq -Rn '[inputs | split("\t") | {key:.[0],before:(.[1] | if . == "~" then null else . end),after:(.[2] | if . == "~" then null else . end)}]' < "$WORK/changes.tsv" > "$WORK/changes.json"
encode "$WORK/previous-state" > "$WORK/previous-state.b64"
encode "$WORK/next-state" > "$WORK/next-state.b64"
jq -Sn --arg scope "$scope" --argjson roots "$roots" --rawfile previous "$WORK/previous-state.b64" --rawfile after "$WORK/next-state.b64" --slurpfile changes "$WORK/changes.json" \
    '{schemaVersion:1,scope:$scope,roots:$roots,previousState:($previous | if .=="~" then null else . end),afterState:$after,changes:$changes[0]}' > "$WORK/next-backup"
transaction=1
atomic_write "$backup_path" "$WORK/next-backup"
for id in "${changes[@]}"; do
    same "${paths[$id]}" "$WORK/before-$id" || fail "File changed during installation: ${paths[$id]}"
    applied+=("$id")
    atomic_write "${paths[$id]}" "${desired[$id]}" "$([[ ${paths[$id]} == "$bin_dir/ai-stack" ]] && printf 1 || printf 0)"
done
atomic_write "$state_path" "$WORK/next-state"
transaction=0
if (( interactive )); then
    printf '\n' >&2; ui_notice success 'Installation complete.'
    if [[ $scope == global ]]; then ui_field 'Next step' "Run $bin_dir/ai-stack and choose Project profile."; fi
    ui_line 'Start a fresh Codex session to load the selected content.' "$ui_muted"
    printf '\n' >&2
else printf 'Installed selected content. Client loading and behavior require a separate session check.\n'; fi
