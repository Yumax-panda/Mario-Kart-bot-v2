.PHONY: stamp
stamp: # mark DB as already at head without running DDL (make stamp url="mysql://user:pass@host:port/db")
	@poetry run alembic $(if $(url),-x db_url="$(url)") stamp head

.PHONY: check
check: # check for differences between models and DB (make check url="mysql://user:pass@host:port/db")
	@poetry run alembic $(if $(url),-x db_url="$(url)") check
