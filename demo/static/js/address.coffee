map = L.map('map').setView([60.184167, 24.949167], 11)
layer = L.tileLayer('http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/997/256/{z}/{x}/{y}.png',
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>'
)
layer.addTo(map)

#stamen_layer = new L.StamenTileLayer("watercolor")
#stamen_layer.addTo(map)

marker = null
input_addr_map = null

$("#address-input").typeahead(
    source: (query, process_cb) ->
        url_query = encodeURIComponent(query)
        $.getJSON(API_PREFIX + 'v1/address/?format=json&name=' + url_query, (data) ->
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
    url = API_PREFIX + "v1/address/?format=json&lat=#{ coords[0] }&lon=#{ coords[1] }"
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
    match_obj = null
    for obj in input_addr_map
        if obj.name == $(this).val()
            match_obj = obj
            break
    if not match_obj
        return
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

input_district_map = null
$("#district-input").typeahead(
    source: (query, process_cb) ->
        $.getJSON(API_PREFIX + 'v1/district/', {input: query}, (data) ->
            objs = data.objects
            ret = []
            input_addr_map = []
            for obj in objs
                ret.push(obj.name)
            input_district_map = objs
            process_cb(ret)
        )
)


$("#district-input").on 'change', ->
    match_obj = null
    for obj in input_district_map
        if obj.name == $(this).val()
            match_obj = obj
            break
    if not match_obj
        return
    borders = L.geoJson match_obj.borders,
        style:
            weight: 2
    borders.bindPopup match_obj.name
    borders.addTo map
    map.fitBounds borders.getBounds()

show_plans = false
$("#show-plans").on 'click', ->
    show_plans = true
    refresh_plans()

map.on 'moveend', (ev) ->
    if show_plans
        refresh_plans()

plans = {}

refresh_plans = ->
    bounds = map.getBounds().toBBoxString()
    $.getJSON API_PREFIX + 'v1/plan/', {bbox: bounds, limit: 100}, (data) ->
        for obj in data.objects
            if obj.id of plans
                continue
            plans[obj.id] = obj
            geom = L.geoJson obj.geometry,
                style:
                    weight: 2
            geom.bindPopup "Kaava nr. <b>#{obj.origin_id}</b>"
            geom.addTo map
