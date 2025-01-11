-- Use thread-local variables to maintain sequence across requests
math.randomseed(os.time()) -- Initialize random seed

-- Initialize thread state
function setup(thread)
    thread:set("request_index", 1) -- Start from the first request type
end

-- Generate a random string of the specified length
function random_string(length)
    local chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    local result = ''
    for i = 1, length do
        local rand_index = math.random(1, #chars)
        result = result .. chars:sub(rand_index, rand_index)
    end
    return result
end

-- Generate a random severity
function random_severity()
    local severities = {"major", "minor", "critical", "warning"}
    return severities[math.random(1, #severities)]
end

-- Generate a random event time
function random_event_time()
    local year = math.random(2000, 2030)
    local month = string.format("%02d", math.random(1, 12))
    local day = string.format("%02d", math.random(1, 28))
    local hour = string.format("%02d", math.random(0, 23))
    local minute = string.format("%02d", math.random(0, 59))
    local second = string.format("%02d", math.random(0, 59))
    return string.format("%d-%s-%sT%s:%s:%sZ", year, month, day, hour, minute, second)
end

-- Generate a random JSON body
function random_json_body()
    local length = math.random(10, 100) -- Randomize the length of content
    return string.format('{
        "ietf-https-notif:notification": {
            "eventTime": "%s",
            "event": {
                "event-class": "fault",
                "reporting-entity": {
                    "card": "%s"
                },
                "severity": "%s"
            }
        }
    }', random_event_time(), random_string(length), random_severity())
end

-- Generate a random XML body
function random_xml_body()
    local length = math.random(10, 100) -- Randomize the length of content
    return string.format('
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
  <eventTime>%s</eventTime>
  <event>
    <event-class>fault</event-class>
    <reporting-entity>
      <card>%s</card>
    </reporting-entity>
    <severity>%s</severity>
  </event>
</notification>
', random_event_time(), random_string(length), random_severity())
end

-- Request types
local request_types = {
    function() -- Correct GET request
        wrk.method = "GET"
        wrk.path = "/capabilities"
        wrk.body = nil
        wrk.headers["Content-Type"] = nil
    end,

    function() -- Correct JSON POST
        wrk.method = "POST"
        wrk.path = "/relay-notification"
        wrk.body = random_json_body()
        wrk.headers["Content-Type"] = "application/json"
    end,

    function() -- Malformed JSON POST
        wrk.method = "POST"
        wrk.path = "/relay-notification"
        wrk.body = '{"ietf-https-notif:notification": {"eventTime": "2013-12-21T00:01:00Z"' -- Missing brackets
        wrk.headers["Content-Type"] = "application/json"
    end,

    function() -- Correct XML POST
        wrk.method = "POST"
        wrk.path = "/relay-notification"
        wrk.body = random_xml_body()
        wrk.headers["Content-Type"] = "application/xml"
    end,

    function() -- Malformed XML POST
        wrk.method = "POST"
        wrk.path = "/relay-notification"
        wrk.body = '<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
                      <eventTime>2013-12-21T00:01:00Z</eventTime>' -- Missing closing tags
        wrk.headers["Content-Type"] = "application/xml"
    end,

    function() -- 404 GET request
        wrk.method = "GET"
        wrk.path = "/nonexistent-endpoint"
        wrk.body = nil
        wrk.headers["Content-Type"] = nil
    end
}

-- Select a request type in sequence for each call
function request()
    local index = wrk.thread:get("request_index")
    request_types[index]()
    index = index + 1
    if index > #request_types then
        index = 1 -- Loop back to the first request type
    end
    wrk.thread:set("request_index", index)
    return wrk.format(nil)
end

