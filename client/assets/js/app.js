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
      'ya.nouislider'
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

  /*Player Controller for seekbar, backward/play/forward buttons and volume control */
  app.controller('PlaybackCtrl', function($scope) {
      $scope.seekbarOptions = {
        start: [0],
        range: {min: 0, max: 100}
      }
      $scope.volumeControlOptions = {
        start: [100],
        range: {min: 0, max: 100}
      }
    })


})();



