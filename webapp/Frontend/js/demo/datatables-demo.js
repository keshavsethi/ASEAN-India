var table = $('#table1').DataTable ( {

} );
var alerttable = $('#alert').DataTable ( {

} );

const config = {
  apiKey: "AIzaSyCqOdIjUsNL95Uc00JBmhUWgHXtWCtNTLU",
  authDomain: "health-care-iot-534c9.firebaseapp.com",
  databaseURL: "https://health-care-iot-534c9.firebaseio.com",
  projectId: "health-care-iot-534c9",
  storageBucket: "health-care-iot-534c9.appspot.com",
  messagingSenderId: "214130811754",
  appId: "1:214130811754:web:a15dbec4a135da9b3d7b13",
  measurementId: "G-3ZLX17QWM7"
};
firebase.initializeApp(config);
let values = [];
let ids = [];
let time= [];

firebase.database().ref('data/temp').limitToLast(200).on('value', ts_measures => {
  ts_measures.forEach(ts_measure => {
  values.push(ts_measure.val());
  });
  for(i=1;i<=values.length;i++){
      ids[i-1]=i;
  }
  });

  firebase.database().ref('data/time').limitToLast(200).on('value', ts_measures => {
    ts_measures.forEach(ts_measure => {
    time.push(ts_measure.val());
    });
  });
    
  firebase.database().ref('data/pulse').limitToLast(200).on('value', ts_measures => {
    let i=0;
    ts_measures.forEach(ts_measure => {
      values.push(ts_measure.val());
      var dataSet = [time[i], values[i],ts_measure.val()];
      table.rows.add([dataSet]).draw();
      i++;
      }); 
    });
