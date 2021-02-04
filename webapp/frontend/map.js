$("#button_mmsi").click(function(){
  mmsi = document.getElementById('mmsi').value;console.log(mmsi);

	let requestUrl = "https://raw.githubusercontent.com/keshavsethi/LSTM/master/LSTM/Jsons/"+ mmsi +".json"; 
	// let requestUrl = "https://raw.githubusercontent.com/keshavsethi/LSTM/master/LSTM/waka.json" 
	url_post = "http://127.0.0.1:5000/predict_withone";

	 $.getJSON(requestUrl
	    ,function(data){
	      console.log(data);
		//data.filter(x.speed => !!x.speed);
		data.sort(function(a, b){
		   return new Date(b['# Timestamp']) - new Date(a["# Timestamp"]);
	      });

		data_raw = [];
		course_raw  = [];
		rot_raw  = [];
		lat_raw =[];
		long_raw =[];
		heading_raw = [];
		let index = 0;
		for(let index1 in data){
		  data_raw.push({ timestamp: data[index1]["# Timestamp"], speed: data[index1].SOG });
		  course_raw.push({ timestamp: data[index1]["# Timestamp"], course: data[index1].COG });
		  rot_raw.push({ timestamp: data[index1]["# Timestamp"], rot: data[index1].ROT });
		  lat_raw.push({ timestamp: data[index1]["# Timestamp"], lat: data[index1].Latitude });
		  long_raw.push({ timestamp: data[index1]["# Timestamp"], long: data[index1].Longitude });
		  heading_raw.push({ timestamp: data[index1]["# Timestamp"], heading: data[index1].Heading });
		  index++;
		}
		data_raw.reverse();
		course_raw.reverse();
		rot_raw.reverse();
		lat_raw.reverse();
		long_raw.reverse();
		heading_raw.reverse();
	let timestamp = data_raw.map(function (val) { return val['timestamp']; });
	console.log(timestamp);
	let speed = data_raw.map(function (val) { return val['speed']; });
	let course = course_raw.map(function (val) { return val['course']; });
	let rot = rot_raw.map(function (val) { return val['rot']; });
	let lat = lat_raw.map(function (val) { return val['lat']; });
	let long = long_raw.map(function (val) { return val['long']; });
	let heading = heading_raw.map(function (val) { return val['heading']; });

	const map = new google.maps.Map(document.getElementById("map"), {
	     zoom: 15,
	    center: { lat: parseFloat(lat[0]), lng: parseFloat(long[0])
 },

	  });
	  let danger = { 
	      path: google.maps.SymbolPath.CIRCLE,
	      scale: 5,
	      fillOpacity: 1,        
	      fillColor: "red",
	      strokeColor:"red"
	    }
	    let ok = { 
	      path: google.maps.SymbolPath.CIRCLE,
	      scale: 5,
	      fillOpacity: 1,        
	      fillColor: "green",
	      strokeColor:"green"
	    }

	    let med = { 
	      path: google.maps.SymbolPath.CIRCLE,
	      scale: 5,
	      fillOpacity: 1,        
	      fillColor: "lightyellow",
	      strokeColor:"lightyellow"
	    }

	// Post function

	async function postData(url = '', data = {}) {
	  const response = await fetch(url, {
	    method: 'POST', 
	    mode: 'cors',
	    cache: 'no-cache', 
	    credentials: 'same-origin', 
	    headers: {
	      'Content-Type': 'application/json'
	    },
	    referrerPolicy: 'no-referrer',
	    body: JSON.stringify(data) 
	  });
	  return response.json();
	}


	  for (let i = 0; i < timestamp.length; i++) {
	    const vessel = data[0].mmsi_label;
	    var position = {
	    x:  [[lat[i]]],
	    y: [[long[i]]]
	    }
	    var param = {
	    a: [[speed[i]]],
	    b: [[course[i]]], 
	    c:  [[rot[i]]],
	    d: [[heading[i]]]
	    }

	    let data1 = {values: [0,0,1,0,parseFloat((param.d[0])[0]), (position.x[0])[0], (position.y[0])[0],parseFloat((param.c[0])[0]), parseFloat((param.a[0])[0]),parseFloat((param.b[0])[0])]};
	let marker;
	postData(url_post, data1)
	  .then(data => {
	console.log(data.Deviation);
	    if(data.Deviation>=1.8){
	     new google.maps.Marker({
	      position: { lat: lat[i], lng: long[i] },
	      map,
	      icon: { 
	      path: google.maps.SymbolPath.CIRCLE,
	      scale: 5,
	      opacity:0.5,
	      fillOpacity: 1,        
	      fillColor: "red",
	      strokeColor:"red"
	    },
	    optimized: false,
	    zIndex: 3,
	      title: timestamp[i],
	    });
	  }
	 if(1<data.Deviation<1.5) {
	     new google.maps.Marker({
	      position: { lat: lat[i], lng: long[i] },
	      map,
	      icon: { 
	      path: google.maps.SymbolPath.CIRCLE,
	      scale: 5,
	      fillOpacity: 1,     
	      opacity:0.5,   
	      fillColor: "yellow",
	      strokeColor:"yellow"
	    },
	    optimized: false,
	    zIndex: 1,
	      title: timestamp[i],
	    });
	}
	else {
	     new google.maps.Marker({
	      position: { lat: lat[i], lng: long[i] },
	      map,
	      icon: { 
	      path: google.maps.SymbolPath.CIRCLE,
	      scale: 5,
	      fillOpacity: 1,        
	      fillColor: "green",
	      strokeColor:"green"
	    },
	    optimized: false,
	    zIndex: 2,
	      title: timestamp[i],
	    });
	}
	  });
	  
	    }

	});
});
