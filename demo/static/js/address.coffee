jQuery ->
    map = L.map('map').setView([60.184167, 24.949167], 11)
    L.tileLayer('http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/997/256/{z}/{x}/{y}.png',
        maxZoom: 18,
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>'
    ).addTo(map)

    marker = null
    input_addr_map = null
    $("#address-input").typeahead(
        source: (query, process_cb) ->
            url_query = encodeURIComponent(query)
            $.getJSON('/api/v1/address/?format=json&name=' + url_query, (data) ->
                objs = data.objects
                ret = []
                input_addr_map = []
                for obj in objs
                    ret.push(obj.name)
                input_addr_map = objs
                process_cb(ret)
            )
    )
    find_nearby_addresses = (coords) ->
        url = "/api/v1/address/?format=json&lat=#{ coords[0] }&lon=#{ coords[1] }"
        $.getJSON(url, (data) ->
            objs = data.objects
            el = $("#nearby-addr-list")
            el.empty()
            for addr in objs
                name = addr.name
                distance = Math.round(addr.distance)
                el.append($("<li>#{ addr.name } #{ distance } m</li>"))
        )
    $("#address-input").on 'change', ->
        console.log $(this).val()
        match_obj = null
        for obj in input_addr_map
            if obj.name == $(this).val()
                match_obj = obj
                break
        if not match_obj
            return
        console.log obj
        coords = obj.location.coordinates
        if not marker
            marker = L.marker([coords[1], coords[0]],
                draggable: true
            )
            marker.on 'dragend', (e) ->
                coords = marker.getLatLng()
                find_nearby_addresses([coords.lat, coords.lng])
            marker.addTo(map)
        else
            marker.setLatLng([coords[1], coords[0]])
        map.setView([coords[1], coords[0]], 17)
