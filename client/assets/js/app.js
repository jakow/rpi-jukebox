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

  /*Service for player control*/

  /*player module*/
  var player = angular.module('player', ['ya.nouislider'])
  .factory('PlayerServices', [function() {

  }]);


  /*Player Controller for desktop seekbar, backward/play/forward buttons and volume control */
  player.controller('PlaybackCtrl', ['$scope', function ($scope) {
    $scope.seekbarOptions = {
      start: [0],
      range: {min: 0, max: 100}
    }
    $scope.volumeControlOptions = {
      start: [100],
      range: {min: 0, max: 100}
    }

    $scope.playing = false; //true if playback is on, false if playback is off

    $scope.play = function play() {
      $scope.playing = !($scope.playing); //toggle for testing
    }
  }]);
})();



