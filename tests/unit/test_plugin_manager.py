import pytest
from dbt.plugins import PluginManager, dbtPlugin, dbt_hook
from dbt.plugins.manifest import PluginNodes, ModelNodeArgs
from dbt.plugins.contracts import PluginArtifacts, PluginArtifact


class GetNodesPlugin(dbtPlugin):
    @dbt_hook
    def get_nodes(self) -> PluginNodes:
        nodes = PluginNodes()
        nodes.add_model(
            ModelNodeArgs(
                name="test_name",
                package_name=self.project_name,
                identifier="test_identifier",
                schema="test_schema",
            )
        )
        return nodes


class GetArtifactsPlugin(dbtPlugin):
    @dbt_hook
    def get_manifest_artifacts(self, manifest) -> PluginArtifacts:
        return {self.project_name: PluginArtifact()}


class TestPluginManager:
    @pytest.fixture
    def get_nodes_plugin(self):
        return GetNodesPlugin(project_name="test")

    @pytest.fixture
    def get_nodes_plugins(self, get_nodes_plugin):
        return [get_nodes_plugin, GetNodesPlugin(project_name="test2")]

    @pytest.fixture
    def get_artifacts_plugin(self):
        return GetArtifactsPlugin(project_name="test")

    @pytest.fixture
    def get_artifacts_plugins(self, get_artifacts_plugin):
        return [get_artifacts_plugin, GetArtifactsPlugin(project_name="test2")]

    def test_plugin_manager_init_single_hook(self, get_nodes_plugin):
        pm = PluginManager(plugins=[get_nodes_plugin])
        assert len(pm.hooks) == 1

        assert "get_nodes" in pm.hooks
        assert len(pm.hooks["get_nodes"]) == 1
        assert pm.hooks["get_nodes"][0] == get_nodes_plugin.get_nodes

    def test_plugin_manager_init_single_hook_multiple_methods(self, get_nodes_plugins):
        pm = PluginManager(plugins=get_nodes_plugins)
        assert len(pm.hooks) == 1

        assert "get_nodes" in pm.hooks
        assert len(pm.hooks["get_nodes"]) == 2
        assert pm.hooks["get_nodes"][0] == get_nodes_plugins[0].get_nodes
        assert pm.hooks["get_nodes"][1] == get_nodes_plugins[1].get_nodes

    def test_plugin_manager_init_multiple_hooks(self, get_nodes_plugin, get_artifacts_plugin):
        pm = PluginManager(plugins=[get_nodes_plugin, get_artifacts_plugin])
        assert len(pm.hooks) == 2

        assert "get_nodes" in pm.hooks
        assert len(pm.hooks["get_nodes"]) == 1
        assert pm.hooks["get_nodes"][0] == get_nodes_plugin.get_nodes

        assert "get_manifest_artifacts" in pm.hooks
        assert len(pm.hooks["get_manifest_artifacts"]) == 1
        assert pm.hooks["get_manifest_artifacts"][0] == get_artifacts_plugin.get_manifest_artifacts

    def test_get_nodes(self, get_nodes_plugins):
        pm = PluginManager(plugins=get_nodes_plugins)
        nodes = pm.get_nodes()
        assert len(nodes.models) == 2

    def test_get_manifest_artifact(self, get_artifacts_plugins):
        pm = PluginManager(plugins=get_artifacts_plugins)
        artifacts = pm.get_manifest_artifacts(None)
        assert len(artifacts) == 2
