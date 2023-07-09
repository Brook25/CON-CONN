#!/usr/bin/env node


//cities = {'Addis': {'subcities': {'kolfe': {'locatons': ['tor-hailoch', 'ayer-tena']}, 'lafto': { 'locations': ['weyra', 'akaki']}, 'kaliit': { 'locations': ['total', 'mexico', 'golf-club']}}}, 'Hawassa': {'subcities': {'Atote': {'locatons': ['tor-hailoch', 'ayer-tena']}, 'Harar-sefer': { 'locations': ['weyra', 'akaki']}, 'Piassa': { 'locations': ['total', 'mexico', 'golf-club']}}}}


//print(list(cities['Hawassa']['subcities'].keys()))
//let sub_str = "jay";
//let str = "jamjay";
//let new_str = str.replace(sub_str, "")
//str = new_str;
let elem ="hello";
let html = '<a href="{{url_for("views.access_api", loc="eq:' + elem '")}}"><h4>' + elem + '</h4></a>';

console.log(html);
