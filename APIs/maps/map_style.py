# google maps python api doesn't officially support dark mode, so we have to manually set the style on the url itself
# here is the documentation on how to style the map:
# https://developers.google.com/maps/documentation/maps-static/styling
#
# used this as reference as well:
# https://stackoverflow.com/questions/21491222/how-do-i-create-a-dark-google-maps-image-for-google-glass
#
# alternatively, we can also use google maps javascript api (
# https://developers.google.com/maps/documentation/javascript/examples/style-array) to style the map which may look
# cleaner, but that would require a lot of refactoring

google_map_style = "&style=element:geometry|invert_lightness:true&style=element:labels.text.stroke|color:0x242f3e" \
                   "&style=feature:poi|element:geometry.fill|color:0x404040&style=feature:poi.park|element" \
                   ":geometry|color:0x263c3f&style=feature:road|element:geometry|color:0x38414e&style=feature:road" \
                   "|element:geometry.stroke|color:0x212a37&style=feature:road|element:labels.text.fill|color" \
                   ":0x9ca5b3&style=feature:road.highway|element:geometry|color:0x746855&style=feature:road.highway" \
                   "|element:geometry.stroke|color:0x1f2835&style=feature:road.highway|element:labels.text.fill|color" \
                   ":0xf3d19c&style=feature:transit|element:geometry|color:0x2f3948&style=feature:transit.station" \
                   "|element:labels.text.fill|color:0xd59563&style=feature:water|element:geometry|color:0x17263c" \
                   "&style=feature:water|element:labels.text.fill|color:0x515c6d&style=feature:water|element:labels" \
                   ".text.stroke|color:0x17263c&style=feature:landscape|element:geometry|visibility:on&style=feature" \
                   ":landscape|element:geometry.fill|color:0x242f3e"
