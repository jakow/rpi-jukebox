//(function () {
'use strict';

var app = angular.module('application', [
  /*dependencies of the application*/
  'ui.router',
  'ngAnimate',
  //foundation
  'foundation',
  'foundation.dynamicRouting',
  'foundation.dynamicRouting.animations',

  //my stuff
  'ya.nouislider',
  'player',
  'search'
]);

(function () {
  app
    .config(config)
    .run(run)
  ;


  config.$inject = ['$urlRouterProvider', '$locationProvider'];

  function config($urlProvider, $locationProvider) {
    $urlProvider
      .otherwise('/');

    $locationProvider.html5Mode({
      enabled: false,
      requireBase: false
    });

    $locationProvider.hashPrefix('!');
  }

  function run() {
    FastClick.attach(document.body);
  }


})();

//})();

var player = angular.module('player', ['ya.nouislider'])
  .factory('playerService', ['$http', '$log', '$interval', function ($http, $log, $interval) {
    /*create the player service object*/
    var p = {};

    /* helpers */
    p.state = {};
    p.updateState = function (xhrResponse) {
      p.state = xhrResponse.data;
      $log.log(p.state);
    }

    p.logError = function (error) {
      $log.log('Error: ' + error);
    }

    p.refresh = function () {
      $log.log("Refreshing");
      $http.get('json_state').then(p.updateState, p.logError);
    }

    /* the autoRefresh promise object uses interval service will update state of the player every 5 seconds.
     This should probably be reworked, so that state is updated on server-side events */

    /*send commands to the player. Each command returns state that updates the local state */
    p.stopRefresh = function () {
      $interval.cancel(p.autoRefresh);
    }

    p.request = function (req) {
      return $http.get(req).then(
        function (response) { //success callback
          /* if successfully fetched, transform the xhrResponse to just return data */
          //p.updateState(response); //slows things down a bit
          return response.data;
        });
    }

    p.playPause = function () {
      console.log('Requesting play/pause');
      return p.request('play_pause');
    }

    p.rewind = function () {
      console.log('Requesting rewind');
      return p.request('rewind');
    }

    p.addToQueue = function (songData) {

    }


    return p;
  }]);

var search = angular.module('search', ['YtAPI'])
  .factory('rpjYoutube', ['Youtube', '$window', function (Youtube, $window) {
    var rpjYt = {};
    //persistent storage of last fetched result
    rpjYt.lastResult = {};
    rpjYt.lastQuery = {};

    rpjYt.ready = function () {
      return Youtube._gapiLoaded;
    }
    rpjYt.search = function (query) {
      rpjYt.decorateQuery(query);
      return Youtube.search(query).then(function (response) {
        rpjYt.results = response; // save response to be used later
        return response;
      });
    };
    rpjYt.isEmptyQuery = function (query) {
      for (var key in query) {
        if (query.hasOwnProperty(key)) return false;
      }
      return true;
    };

    //store default search settings to be reused. In the future they will be xhr'd from server-side config file
    rpjYt.searchSettings = {
      part: 'snippet',
      maxResults: 10
    };

    //decorate query with searchSettings that were not overriden
    rpjYt.decorateQuery = function (query) {
      for (var setting in rpjYt.searchSettings) {
        if (!query.hasOwnProperty(setting)) {
          query[setting] = rpjYt.searchSettings[setting];
        }
      }
    };

    return rpjYt;
  }])
  ;





