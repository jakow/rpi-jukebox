function initGAPI() {
  console.log('Initialising gapi');
  //window.initGapi();
}

angular.module('YtAPI', [])
  .factory('Youtube', ['$log', '$window', function ($log, $window) {
    var Yt = {};
    $window.initGapi = function () {
      gapi.client.load('youtube', 'v3').then(function () {
        gapi.client.setApiKey(apiKey);
      });
    }
    Yt.search = function(query) {
      return gapi.client.search.list(query);
    }
    return Yt;
  }
  ])
;
