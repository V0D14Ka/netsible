from nornir_napalm.plugins.tasks import napalm_get
from netsible.modules import BasicModule
from netsible.utils.utils import Display, get_default_dir
from netsible.utils.nornir_loader import load_nornir


class NapalmGetFacts(BasicModule):
    def run(self, task_name, client_info, module, params, sensitivity):
        host_filter = client_info.get("name") or client_info.get("host")

        Display.debug(f"[napalm_get_facts] Target host: {host_filter}")

        try:
            nr = load_nornir(get_default_dir() / "config.yaml")
            nr = nr.filter(name=host_filter)

            result = nr.run(task=napalm_get, getters=["facts"])

            for host, res in result.items():
            # res is a MultiResult
                if res.failed:
                    Display.error(f"[{host}] Task failed.")

                    # Распечатать все результаты по задачам для хоста
                    for sub_result in res:
                        if sub_result.failed:
                            Display.error(f"[{host}] Subtask '{sub_result.name}' failed with exception:")
                            Display.error(f"{sub_result.exception}")
                    continue
                    continue

                napalm_result = res[0].result  # First Result inside MultiResult

                if isinstance(napalm_result, dict):
                    facts = napalm_result.get("facts", {})
                    Display.debug(f"[{host}] Hostname: {facts.get('hostname')}")
                    Display.debug(f"[{host}] OS version: {facts.get('os_version')}")
                    Display.debug(f"[{host}] Model: {facts.get('model')}")
                    Display.debug(f"[{host}] Serial: {facts.get('serial_number')}")
                else:
                    Display.error(f"[{host}] Unexpected result type: {type(napalm_result)}")

                return 200
        except Exception as e:
            Display.error(f"[napalm_get_facts] Failed to get facts for {host_filter}: {e}")
            return 401 if sensitivity == "yes" else 500
