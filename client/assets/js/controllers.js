/**
 * Created by jakub on 24/12/15.
 */

  /*Player Controller for desktop seekbar, backward/play/forward buttons and volume control */
  player.controller('PlaybackCtrl', ['$scope', 'playerService', function ($scope, playerService) {

    /* register watcher for service state */
    $scope.playing = playerService.state.isPlaying;
    $scope.$watch(
      function() {return playerService.state},
      function(newState) {
        $scope.playing = newState.isPlaying;
      },
      false);

    $scope.seekbarOptions = {
      start: [0],
      range: {min: 0, max: 100}
    }
    $scope.volumeControlOptions = {
      start: [100],
      range: {min: 0, max: 100}
    }

    $scope.$on('destroy', function() {
      playerService.stopRefresh();
    });
    $scope.pause = function() {
      $scope.playing = !$scope.playing;

      //$scope.playing = !$scope.playing;
      playerService.pause().then(function(response) {
        $scope.playing = response.playing;
        console.log('paused/unpaused successfully');
      })
    }
  }]);

  player.controller('QueueCtrl', ['$scope', 'playerService', function($scope, playerService) {
    $scope.nowPlaying = playerService.state.nowPlaying;
    $scope.queue = playerService.state.queue;
    $scope.$watch(
      function() {return playerService.state},
      function(newState) {
        $scope.nowPlaying = newState.nowPlaying;
        $scope.queue = newState.queue;
      },
      false);
    //$http.get('assets/test/sampleQueue.json').then(function(response) { $scope.queue = response}, function() {});



  }]);
