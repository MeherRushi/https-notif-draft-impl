-- Persistent counter for each thread
local counter = 0

-- Initialize the thread
function init(args)
    counter = 0  -- Start the counter at 0 for each thread
end

-- Request sequence logic
function request()
    counter = counter + 1  -- Increment the counter for each request

    -- Handle the sequence of requests
    if counter == 1 then
        wrk.method = "GET"
        wrk.path = "/capabilities"
        return wrk.format(nil)
    elseif counter == 2 then
        wrk.method = "POST"
        wrk.path = "/relay-notification"
        wrk.body = '{"ietf-https-notif:notification": {"eventTime": "2013-12-21T00:01:00Z", "event": {"event-class": "fault", "reporting-entity": {"card": "Ethernet0"}, "severity": "major"}}}'
        wrk.headers["Content-Type"] = "application/json"
        return wrk.format(nil)
    elseif counter == 3 then
        wrk.method = "POST"
        wrk.path = "/relay-notification"
        wrk.body = '{"ietf-https-notif:notification": {"eventTime": "2013-12-21T00:01:00Z", "event": {"event-class": "fault"}}'  -- Malformed JSON
        wrk.headers["Content-Type"] = "application/json"
        return wrk.format(nil)
    elseif counter == 4 then
        wrk.method = "POST"
        wrk.path = "/relay-notification"
        wrk.body = [[
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
  <eventTime>2013-12-21T00:01:00Z</eventTime>
  <event>
    <event-class>fault</event-class>
    <reporting-entity>
      <card>Ethernet0</card>
    </reporting-entity>
    <severity>major</severity>
  </event>
</notification>
]]
        wrk.headers["Content-Type"] = "application/xml"
        return wrk.format(nil)
    elseif counter == 5 then
        wrk.method = "POST"
        wrk.path = "/relay-notification"
        wrk.body = [[
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
  <eventTime>2013-12-21T00:01:00Z</eventTime>
  <event>
    <event-class>fault</event-class>
    <reporting-entity>
      <card>Ethernet0</card>
    </reporting-entity>
]]  -- Malformed XML
        wrk.headers["Content-Type"] = "application/xml"
        return wrk.format(nil)
    elseif counter == 6 then
        wrk.method = "GET"
        wrk.path = "/nonexistent-endpoint"
        return wrk.format(nil)
    else
        counter = 0  -- Reset the counter after the last request
        return request()  -- Restart the sequence
    end
end

