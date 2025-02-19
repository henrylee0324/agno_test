@echo off
echo Neo4j container starting...
docker start neo4j-apoc
if %ERRORLEVEL% neq 0 (
    echo Neo4j container not found, creating...
    docker run -d -p 7474:7474 -p 7687:7687 ^
        -v "C:/Users/henry/neo4j-data:/data" ^
        -v "C:/Users/henry/neo4j-plugins:/plugins" ^
        --name neo4j-apoc ^
        -e NEO4J_apoc_export_file_enabled=true ^
        -e NEO4J_apoc_import_file_enabled=true ^
        -e NEO4J_apoc_import_file_use__neo4j__config=true ^
        -e NEO4J_PLUGINS="[\"apoc\",\"apoc-extended\"]" ^
        neo4j:latest
)

echo Neo4j successfully started!
echo http://localhost:7474
