# Installation compatibility fixture

`schema1-migration.json` provides the former version and opaque retired-file
contents for a schema-1 migration test. The test constructs the prior ownership
state in temporary directories, then verifies Bash updates, conflict protection,
record preservation and byte-exact rollback. The placeholder bytes are data;
no historical installer is retained or executed. This is a synthetic compatibility
fixture, not a reproduction of the previous Python runtime.
