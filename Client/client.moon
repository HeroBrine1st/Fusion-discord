json = require "JSON"
internet = require "internet"
component = require "component"
event = require "event"

properties =
    pwd: "12345678",
    name: "ship",
    remote_address: "0.0.0.0",
    remote_port: 0,
    event_blacklist: {"internet_ready", "touch", "drag", "drop", "scroll", "redstone_changed", "key_up", "key_down", "clipboard", "chat_message"}

json_encode = (tbl) ->
    return "#{json.encode(tbl)}\n"

conn = internet.socket(properties.remote_address, properties.remote_port)

conn_write = (data) ->
    conn\write data
    print(">>> " .. data\gsub("\n", ""))

process_method = (root, ...) ->
    args = {...}
    success, _next = pcall(() -> 
    	root[table.remove(args,1)]
    )
    if not success
    	return success, _next
    local process_function
    if type(_next)  == "function"
        process_function = pcall
    elseif type(_next) == "table"
        if getmetatable(_next) and getmetatable(_next).__call
            process_function = pcall
        else
            process_function = process_method
    else
        return nil, "Invalid method"
    return process_function _next, table.unpack args
 
elem_in = (tbl, elem) ->
    for tblelem in *tbl
        if tblelem == elem
            return true
    return false

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
            conn\write json_encode {
                "ping_response": true,
                "hash": data.hash
            }
        elseif data.request == "execute"
            func, reason = load data.data, "=protocol_input"
            if not func
                response =
                    hash: data.hash
                    response: {reason}
                    "error": true
                conn_write json_encode response
            else
                results = {pcall(func)}
                response =
                    hash: data.hash
                    response: {table.unpack(results,2,#results)}
                    "error": not results[1]
                conn_write json_encode response]
        elseif data.request == "exit"
            return
        else
            print("<<< " .. json_data\gsub("\n", ""))
            response_data = {process_method(package.loaded, table.unpack(data.request))}
            if not response_data[1]
            	response_data[2] = debug.traceback(response_data[2])
            response =
                hash: data.hash
                response: {table.unpack(response_data,2,#response_data)}
                "error": not response_data[1]
            conn_write json_encode response
    e = {event.pull(0)}
    while #e > 0
        if not elem_in(properties.event_blacklist, e[1])
            conn_write json_encode {"event": e}
        e = {event.pull(0)}
conn\close!
