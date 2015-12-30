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
      'player'
    ])
    .config(config)
    .run(run)
    ;


  config.$inject = ['$urlRouterProvider', '$locationProvider'];

  function config($urlProvider, $locationProvider) {
    $urlProvider.otherwise('/');

    $locationProvider.html5Mode({
      enabled: false,
      requireBase: false
    });

    $locationProvider.hashPrefix('!');
  }

  function run() {
    FastClick.attach(document.body);
  }

  /* my stuff */


  /*player module to detach foundation's js from player*/

  /* player service is the service for playback control via XHR */
  var player = angular.module('player', ['ya.nouislider'])
    .factory('playerService', ['$http', '$log', '$interval', function ($http, $log, $interval) {
      /*create the player service object*/
      var p = {};

      /* helpers */
      p.updateState = function (xhrResponse) {
        p.state = xhrResponse.data;
        $log.log(p.state);
      }

      p.logError = function (error) {
        $log.log('Error: ' + error);
      }

      p.request = function (command) {
        $log.log("Requested " + command);
        $http.get(command).then(p.updateState, p.logError);
      }

      /* the autoRefresh promise object uses interval service will update state of the player every 5 seconds.
       This should probably be reworked, so that state is updated on server-side events */
      p.autoRefresh = $interval(function() {p.request('json_state');}, 10000, 5);
      /*send commands to the player. Each command returns state that updates the local state */
      p.stopRefresh = function() {
        $interval.cancel(p.autoRefresh);
      }

      p.pauseResume = function () {
        console.log('Requesting play/pause');
        p.request('pause');
      };
      p.addToQueue = function (songData) {

      }

      return p;
    }])
    .run(function(playerService){

    });  // eager instatiation of player service


  /*Player Controller for desktop seekbar, backward/play/forward buttons and volume control */
  player.controller('PlaybackCtrl', ['$scope', 'playerService', function ($scope, playerService) {
    console.log('playback ctrl started');
    $scope.playerState = playerService.state;
    playerService.request('json_state');
    console.log($scope.playerState);
    $scope.seekbarOptions = {
      start: [0],
      range: {min: 0, max: 100}
    }
    $scope.volumeControlOptions = {
      start: [100],
      range: {min: 0, max: 100}
    }

    $scope.$on('destroy', function() {
      player.stopRefresh();
    });
    $scope.pauseResume = function() {
      console.log('play button pressed');
      playerService.pauseResume();
    }
  }]);
})();


