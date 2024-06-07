import os
from variables import PROXY_PASSWORD


# def create_proxy_auth_plugin(plugin_dir: str, proxy_user: str, proxy_host: str, proxy_port: str):
#     manifest_json = """
#     {
#         "version": "1.0.0",
#         "manifest_version": 2,
#         "name": "Chrome Proxy",
#         "permissions": [
#             "proxy",
#             "tabs",
#             "unlimitedStorage",
#             "storage",
#             "<all_urls>",
#             "webRequest",
#             "webRequestBlocking"
#         ],
#         "background": {
#             "scripts": ["background.js"]
#         },
#         "minimum_chrome_version":"22.0.0"
#     }
#     """
#
#     background_js = f"""
#     var config = {{
#             mode: "fixed_servers",
#             rules: {{
#             singleProxy: {{
#                 scheme: "http",
#                 host: "{proxy_host}",
#                 port: parseInt("{proxy_port}")
#             }},
#             bypassList: ["localhost", "127.0.0.1"]
#             }}
#         }};
#
#     chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
#
#     function callbackFn(details) {{
#         return {{
#             authCredentials: {{
#                 username: "{proxy_user}",
#                 password: "{PROXY_PASSWORD}"
#             }}
#         }};
#     }}
#
#     chrome.webRequest.onAuthRequired.addListener(
#                 callbackFn,
#                 {{urls: ["<all_urls>"]}},
#                 ['blocking']
#     );
#     """
#
#     # Create plugin directory if it doesn't exist
#     if not os.path.exists(plugin_dir):
#         os.makedirs(plugin_dir)
#     # Write manifest.json and background.js to the plugin directory
#     with open(os.path.join(plugin_dir, "manifest.json"), 'w') as f:
#         f.write(manifest_json)
#     with open(os.path.join(plugin_dir, "background.js"), 'w') as f:
#         f.write(background_js)
#     return True


# DEBUG
def create_proxy_auth_plugin(plugin_dir: str, proxy_user: str, proxy_host: str, proxy_port: str):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = f"""
        var config = {{
                mode: "fixed_servers",
                rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: parseInt("{proxy_port}")
                }},
                bypassList: ["localhost", "127.0.0.1"]
                }}
            }};

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy_user}",
                    password: "{PROXY_PASSWORD}"
                }}
            }};
        }}

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {{urls: ["<all_urls>"]}},
                    ['blocking']
        );
        """

    # Create plugin directory if it doesn't exist
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)
    # Write manifest.json and background.js to the plugin directory
    with open(os.path.join(plugin_dir, "manifest.json"), 'w') as f:
        f.write(manifest_json)
    with open(os.path.join(plugin_dir, "background.js"), 'w') as f:
        f.write(background_js)
    return True
