let input_dataset = [];
let result = [];
let data_raw = [];
let sma_vec = [];
let window_size = 50;
let trainingsize = 70;
let data_temporal_resolutions = 'speed';

$(document).ready(function(){
  $('select').formSelect();
});


function onClickChangeDataFreq(freq){
  console.log(freq.value);
  data_temporal_resolutions = freq.value;
}

function onClickFetchData(){

  $("#btn_fetch_data").hide();
  $("#load_fetch_data").show();

  let requestUrl = "https://raw.githubusercontent.com/keshavsethi/streamlit/master/csvjson.json";

  $.getJSON(requestUrl
    ,function(data){
      //console.log(data[0])
      let message = "";
      $("#div_container_linegraph").show();
      // "daily" is data for me

      if(data){
        data.sort(function(a, b){
           return new Date(b.timestamp) - new Date(a.timestamp);
      });
        data_raw = [];
        sma_vec = [];

        let index = 0;
        for(let date in data){
          
          data_raw.push({ timestamp: data[date].timestamp, price: data[date].speed });
          index++;
        }
        console.log(data_raw);

        data_raw.reverse();

        message = "MV Wakashio";

        $("#btn_fetch_data").show();
        $("#load_fetch_data").hide();
        $("#div_linegraph_data_title").text(message);

        if(data_raw.length > 0){
          let timestamps = data_raw.map(function (val) { return val['timestamp']; });
          let prices = data_raw.map(function (val) { return val['price']; });

          let graph_plot = document.getElementById('div_linegraph_data');
          Plotly.newPlot( graph_plot, [{ x: timestamps, y: prices, name: "speed" }], { margin: { t: 0 },  autorange: true,
         showgrid: false,
         zeroline: false,
         showline: false,
         showticklabels: false});
        }

        $("#div_container_getsma").show();
        $("#div_container_getsmafirst").hide();

      }else{
        $("#div_linegraph_data").text( data['Information'] );
      }

    }
  );

}

function onClickDisplaySMA(){
  $("#btn_draw_sma").hide();
  $("#load_draw_sma").show();
  $("#div_container_sma").show();

  window_size = parseInt(document.getElementById("input_windowsize").value);

  sma_vec = ComputeSMA(data_raw, window_size);

  let sma = sma_vec.map(function (val) { return val['avg']; });
  let prices = data_raw.map(function (val) { return val['price']; });

  let timestamps_a = data_raw.map(function (val) { return val['timestamp']; });
  let timestamps_b = data_raw.map(function (val) {
    return val['timestamp'];
  }).splice(window_size, data_raw.length);

  let graph_plot = document.getElementById('div_linegraph_sma');
  Plotly.newPlot( graph_plot, [{ x: timestamps_a, y: prices, name: "Speed" }], { margin: { t: 0 } } );
  Plotly.plot( graph_plot, [{ x: timestamps_b, y: sma, name: "SMA" }], { margin: { t: 0 } } );

  $("#div_linegraph_sma_title").text("Speed and Simple Moving Average (window: " + window_size + ")" );
  $("#btn_draw_sma").show();
  $("#load_draw_sma").hide();

  $("#div_container_train").show();
  $("#div_container_trainfirst").hide();

  displayTrainingData();
}


function displayTrainingData(){
  $("#div_container_trainingdata").show();

  let set = sma_vec.map(function (val) { return val['set']; });
  let data_output = "";
  for (let index = 0; index < 25; index++)
  {
     data_output += "<tr><td width=\"20px\">" + (index + 1) +
      "</td><td>[" + set[index].map(function (val) {
        return (Math.round(val['price'] * 10000) / 10000).toString();
      }).toString() +
      "]</td><td>" + sma_vec[index]['avg'] + "</td></tr>";
  }

  data_output = "<table class='striped'>" +
  "<thead><tr><th scope='col'>#</th>" +
  "<th scope='col'>Input (X)</th>" +
  "<th scope='col'>Label (Y)</th></thead>" +
  "<tbody>" + data_output + "</tbody>" +
  "</table>";

  $("#div_trainingdata").html(
    data_output
  );
}



async function onClickTrainModel(){

  let epoch_loss = [];

  $("#div_container_training").show();
  $("#btn_draw_trainmodel").hide();

  document.getElementById("div_traininglog").innerHTML = "";

  let inputs = sma_vec.map(function(inp_f){
    return inp_f['set'].map(function(val) { return val['price']; })
  });
  let outputs = sma_vec.map(function(outp_f) { return outp_f['avg']; });

  trainingsize = parseInt(document.getElementById("input_trainingsize").value);
  let n_epochs = parseInt(document.getElementById("input_epochs").value);
  let learningrate = parseFloat(document.getElementById("input_learningrate").value);
  let n_hiddenlayers = parseInt(document.getElementById("input_hiddenlayers").value);

  inputs = inputs.slice(0, Math.floor(trainingsize / 100 * inputs.length));
  outputs = outputs.slice(0, Math.floor(trainingsize / 100 * outputs.length));

  let callback = function(epoch, log) {
    let logHtml = document.getElementById("div_traininglog").innerHTML;
    logHtml = "<div>Epoch: " + (epoch + 1) + " (of "+ n_epochs +")" +
      ", loss: " + log.loss +
      // ", difference: " + (epoch_loss[epoch_loss.length-1] - log.loss) +
      "</div>" + logHtml;

    epoch_loss.push(log.loss);

    document.getElementById("div_traininglog").innerHTML = logHtml;
    document.getElementById("div_training_progressbar").style.width = Math.ceil(((epoch + 1) * (100 / n_epochs))).toString() + "%";
    document.getElementById("div_training_progressbar").innerHTML = Math.ceil(((epoch + 1) * (100 / n_epochs))).toString() + "%";

    let graph_plot = document.getElementById('div_linegraph_trainloss');
    Plotly.newPlot( graph_plot, [{x: Array.from({length: epoch_loss.length}, (v, k) => k+1), y: epoch_loss, name: "Loss" }], { margin: { t: 0 } } );
  };

  console.log('train X', inputs)
  console.log('train Y', outputs)
  result = await trainModel(inputs, outputs, window_size, n_epochs, learningrate, n_hiddenlayers, callback);

  let logHtml = document.getElementById("div_traininglog").innerHTML;
  logHtml = "<div>Model train completed</div>" + logHtml;
  document.getElementById("div_traininglog").innerHTML = logHtml;

  $("#div_container_validate").show();
  $("#div_container_validatefirst").hide();
  $("#div_container_predict").show();
  $("#div_container_predictfirst").hide();

}

function onClickValidate() {

  $("#div_container_validating").show();
  $("#load_validating").show();
  $("#btn_validation").hide();

  let inputs = sma_vec.map(function(inp_f) {
   return inp_f['set'].map(function (val) { return val['price']; });
  });

  // validate on training
  let val_train_x = inputs.slice(0, Math.floor(trainingsize / 100 * inputs.length));
  // let outputs = sma_vec.map(function(outp_f) { return outp_f['avg']; });
  // let outps = outputs.slice(0, Math.floor(trainingsize / 100 * inputs.length));
  console.log('val_train_x', val_train_x)
  let val_train_y = makePredictions(val_train_x, result['model']);
  console.log('val_train_y', val_train_y)

  // validate on unseen
  let val_unseen_x = inputs.slice(Math.floor(trainingsize / 100 * inputs.length), inputs.length);
  console.log('val_unseen_x', val_unseen_x)
  let val_unseen_y = makePredictions(val_unseen_x, result['model']);
  console.log('val_unseen_y', val_unseen_y)

  let timestamps_a = data_raw.map(function (val) { return val['timestamp']; });
  let timestamps_b = data_raw.map(function (val) {
    return val['timestamp'];
  }).splice(window_size, (data_raw.length - Math.floor((100-trainingsize) / 100 * data_raw.length))); //.splice(window_size, data_raw.length);
  // let timestamps_c = data_raw.map(function (val) {
  //   return val['timestamp'];
  // }).splice(window_size + Math.floor(trainingsize / 100 * val_unseen_x.length), data_raw.length);
  let timestamps_c = data_raw.map(function (val) {
    return val['timestamp'];
  }).splice(window_size + Math.floor(trainingsize / 100 * inputs.length), inputs.length);

  let sma = sma_vec.map(function (val) { return val['avg']; });
  let prices = data_raw.map(function (val) { return val['price']; });
  sma = sma.slice(0, Math.floor(trainingsize / 100 * sma.length));
  console.log('sma', sma)

  let graph_plot = document.getElementById('div_validation_graph');
  Plotly.newPlot( graph_plot, [{ x: timestamps_a, y: prices, name: "Actual Speed" }], { margin: { t: 0 } } );
  Plotly.plot( graph_plot, [{ x: timestamps_b, y: sma, name: "Training Label (SMA)" }], { margin: { t: 0 } } );
  Plotly.plot( graph_plot, [{ x: timestamps_b, y: val_train_y, name: "Predicted (train)" }], { margin: { t: 0 } } );
  Plotly.plot( graph_plot, [{ x: timestamps_c, y: val_unseen_y, name: "Predicted (test)" }], { margin: { t: 0 } } );

  $("#load_validating").hide();
}

async function onClickPredict() {

  $("#div_container_predicting").show();
  $("#load_predicting").show();
  $("#btn_prediction").hide();

  let inputs = sma_vec.map(function(inp_f) {
   return inp_f['set'].map(function (val) { return val['price']; });
  });
  let pred_X = [inputs[inputs.length-1]];
  pred_X = pred_X.slice(Math.floor(trainingsize / 100 * pred_X.length), pred_X.length);
  let pred_y = makePredictions(pred_X, result['model']);

  window_size = parseInt(document.getElementById("input_windowsize").value);

  let timestamps_d = data_raw.map(function (val) {
    return val['timestamp'];
  }).splice((data_raw.length - window_size), data_raw.length);

  // date
  let last_date = new Date(timestamps_d[timestamps_d.length-1]);
  let add_days = 1;
  if(data_temporal_resolutions == 'Weekly'){
    add_days = 7;
  }
  last_date.setDate(last_date.getDate() + add_days);
  let next_date = await formatDate(last_date.toString());
  let timestamps_e = [next_date];

  let graph_plot = document.getElementById('div_prediction_graph');
  Plotly.newPlot( graph_plot, [{ x: timestamps_d, y: pred_X[0], name: "Latest Trends" }], { margin: { t: 0 } } );
  Plotly.plot( graph_plot, [{ x: timestamps_e, y: pred_y, name: "Predicted Speed" }], { margin: { t: 0 } } );

  $("#load_predicting").hide();
}

function ComputeSMA(data, window_size)
{
  let r_avgs = [], avg_prev = 0;
  for (let i = 0; i <= data.length - window_size; i++){
    let curr_avg = 0.00, t = i + window_size;
    for (let k = i; k < t && k <= data.length; k++){
      curr_avg += data[k]['price'] / window_size;
    }
    r_avgs.push({ set: data.slice(i, i + window_size), avg: curr_avg });
    avg_prev = curr_avg;
  }
  return r_avgs;
}

function formatDate(date) {
  var d = new Date(date),
      month = '' + (d.getMonth() + 1),
      day = '' + d.getDate(),
      year = d.getFullYear();

  if (month.length < 2) month = '0' + month;
  if (day.length < 2) day = '0' + day;

  return [year, month, day].join('-');
}
