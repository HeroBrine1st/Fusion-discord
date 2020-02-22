json = require "JSON"
internet = require "internet"
component = require "component"
event = require "event"

properties =
    pwd: "12345678",
    name: "ship",
    remote_address: "0.0.0.0",
    remote_port: 0,
    event_blacklist: {"internet_ready": true, "touch": true, "drag": true, "drop": true, "scroll": true, "redstone_changed": true, 
                      "key_up": true, "key_down": true, "clipboard": true, "chat_message": true}

json_encode = (tbl) ->
    return "#{json.encode(tbl)}\n"

conn = internet.socket(properties.remote_address, properties.remote_port)
while conn
    json_data = conn\read!
    continue if json_data == ""
    if not json_data
        conn = internet.socket(properties.remote_address, properties.remote_port)
    else
        success, data = pcall(json.decode, json_data)
        if not success
            continue
        if data.error
            if data.error == "whois"
                conn\write json_encode(name: properties.name)
            elseif data.error == "service_not_exists"
                print("Wrong configuration: service not exists. We can connect but can't authorize.")
                break
            elseif data.error == "need_authorization"
                print("Authorization")
                conn\write json_encode(auth: properties.pwd)
            elseif data.error == "authorized_user_exists"
                print("Server occupied")
                break
        elseif data.authorized == true
            print("Authorized")
        elseif data.authorized == false
            print("Failed")
            break
        elseif data.request == "ping"
            conn\write json_encode response: "ping"
        elseif data.request == "execute"
            func, reason = load data.data, "=protocol_input"
            if not func
                response =
                    hash: data.hash
                    response: "execute"
                    data: {reason}
                    "error": true
                conn\write json_encode response
            else
                results = {pcall(func)}
                response =
                    hash: data.hash
                    response: "execute"
                    data: {table.unpack(results,2,#results)}
                    "error": not results[1]
                conn\write json_encode response]
        elseif data.request == "exit"
            break
    e = {event.pull(0)}
    while #e > 0
        if not properties.event_blacklist[e[1]]
            conn\write json_encode {"event": e}
        e = {event.pull(0)}
conn\close!
