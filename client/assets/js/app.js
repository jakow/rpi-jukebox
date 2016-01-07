(function () {
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
    ])
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

  app.controller('menuCtrl', ['$scope', function ($scope) {
      $scope.menu = [
        {
          text: "Search",
          iconClass: "search-icon",
          route: "search"
        },
        {
          text: "Settings",
          iconClass: "settings-icon",
          route: "settings"
        }
      ];

      $scope.playlists = [
        {
          name: "Playlist 1",
          iconClass: "note-icon",
          id: "playlist1"
        }


      ];
    }])

    .controller('searchBarCtrl', ['$scope', '$state', '$log', function ($scope, $state, $log) {
      $scope.search = function() {
         $log.log('SEARCHING!!')
      }
    }])
  ;


})();

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
  }]);  // eager instatiation of player service

var searchModule = angular.module('search', ['angular-google-gapi'])
  .factory('ytSearchService', ['$http', '$log', 'GApi', function ($http, $log, GApi) {
    var searchService = {};
    searchService.query = ''
    searchService.search = function(query) {
      /* Search youtube, return a promise */
    };
    return searchService;
  }]);





