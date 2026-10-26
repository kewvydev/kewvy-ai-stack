# Shared JSON and instruction-block operations. File bodies travel as base64.
def begin_marker: "<!-- BEGIN:ai-engineering-stack -->";
def end_marker: "<!-- END:ai-engineering-stack -->";
def managed:
  (. // "") as $text
  | [$text | match("(?:\\A|(?<=\n))" + begin_marker + "\r?\n[\\s\\S]*?(?:\\A|(?<=\n))" + end_marker + "\r?(?=\n|\\z)"; "g")] as $matches
  | if ($text | indices(begin_marker) | length) != ($matches | length)
       or ($text | indices(end_marker) | length) != ($matches | length)
       or ($matches | length) > 1
    then error("Malformed or duplicate stack instruction markers")
    else $matches[0] // null end;
def replace_managed($replacement):
  (. // "") as $text | managed as $old
  | if $old != null then
      $text[0:$old.offset] + ($replacement // "") + $text[$old.offset + $old.length:]
    elif $replacement == null then $text
    else $text + (if $text == "" then "" elif $text | endswith("\n") then "\n" else "\n\n" end)
      + $replacement + "\n" end;
def roots_match($expected; $scope):
  . == $expected or ($scope == "global" and . == ($expected | del(.skills)));
def valid_state($roots; $scope; $kinds; $profiles):
  type == "object" and .schemaVersion == 1 and .scope == $scope
  and (.version | type == "string") and (.roots | roots_match($roots; $scope))
  and (.selection | type == "object" and .client == "codex"
       and (.profile as $id | $profiles | index($id) != null))
  and (.files | type == "object")
  and (if $scope == "global" and (.roots | has("skills") | not)
       then all(.files | keys[]; startswith("skills/") | not) else true end)
  and all(.files | to_entries[];
    .key as $key | .value | type == "object" and .kind != "seed"
    and .kind == $kinds[$key] and (.sha256 | type == "string" and test("^[0-9a-f]{64}$")));
