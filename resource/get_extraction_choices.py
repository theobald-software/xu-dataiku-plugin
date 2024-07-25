import xudataiku.rest


def do(payload, config, plugin_config, inputs):
    ui_parameter_name = payload.get("parameterName")
    if "extraction" == ui_parameter_name:
        xu_server_preset = config.get("xuServerPreset")
        client = xudataiku.rest.Client(xu_server_preset)
        return client.get_extraction_choices()
    if "paramName" == ui_parameter_name:
        #print("payload", payload)
        #print("config", config)
        #print("plugin_config", plugin_config)
        #print("inputs", inputs)
        root_model = payload.get("rootModel")
        extraction = root_model.get("extraction")
        xu_server_preset = extraction.get("xuServerPreset")
        client = xudataiku.rest.Client(xu_server_preset)
        return client.get_parameter_name_choices(extraction.get("extractionName"))
