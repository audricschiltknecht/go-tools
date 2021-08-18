fmt-py-sources: $(wildcard *.py)
	@echo "Formatting Python code"
	@black $<
	@isort $<
	@autoflake -r --in-place --remove-unused-variables $<
