/**
 * Created by jakub on 24/12/15.
 */

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
}]);

/*Player Controller for desktop seekbar, backward/play/forward buttons and volume control */
player.controller('PlaybackCtrl', ['$scope', 'playerService', '$interval', function ($scope, playerService, $interval) {

  /* register watcher for service state */
  $scope.playing = playerService.state.isPlaying;
  playerService.refresh();
  this.autoRefresh = $interval(playerService.refresh, 5000, 0);
  $scope.$watch(
    function () {
      return playerService.state
    },
    function (newState) {
      $scope.playing = newState.isPlaying;
    },
    false);

  $scope.seekbarOptions = {
    start: [0],
    range: {min: 0, max: 100}
  };
  $scope.volumeControlOptions = {
    start: [100],
    range: {min: 0, max: 100}
  };

  $scope.$on('$destroy', function () {
    playerService.stopRefresh();
  });
  $scope.playPause = function () {
    $scope.playing = !$scope.playing;

    //$scope.playing = !$scope.playing;
    playerService.playPause().then(function (response) {
      $scope.playing = response.playing;
      console.log('paused/unpaused successfully');
    })
  };

  $scope.rewind = function () {
    playerService.rewind();
  }
}]);

player.controller('QueueCtrl', ['$scope', 'playerService', '$http', function ($scope, playerService, $http) {
  $scope.nowPlaying = playerService.state.nowPlaying;
  $scope.queue = playerService.state.queue;
  $scope.$watch(
    function () {
      return playerService.state
    },
    function (newState) {
      $scope.nowPlaying = newState.nowPlaying;
      $scope.queue = newState.queue;
    },
    false);
  $http.get('./assets/test/sampleData.json').then(function (response) {
    $scope.queue = response.data.queue;
  });


}]);

search.controller('searchCtrl', ['rpjYoutube', 'playerService', '$scope', '$stateParams', '$window', function (rpjYoutube, playerService, $scope, $stateParams, $window) {
    $scope.loading = false;
    $scope.search = function (query) {
      $scope.loading = true;
      console.log('Searching')
      rpjYoutube.search(query).then(function (response) {
        $scope.result = response.result;
        $scope.loading = false;
        console.log('Search finished');
        console.log($scope.result.items);
        $scope.$apply(); //lags if apply is not called
      });
    };
    $scope.resultsEmpty = function() {
      return rpjYoutube.isEmptyQuery($scope.result);
    }

    //State enter behaviour
    var query = $stateParams;
    if (rpjYoutube.isEmptyQuery(query)) {
      console.log('Query empty');
      $scope.result = rpjYoutube.lastResult;
    }
    else if (!rpjYoutube.ready()) {
      console.log(query);
      $scope.loading = true;
      setTimeout(function () { //wait for yt to be ready!
        $scope.search($stateParams)
      }, 1000);

    }
  else {
      console.log('searching: ' + $stateParams);
      $scope.search($stateParams);
    }
  }])
  .controller('searchBarCtrl', ['rpjYoutube', '$scope', '$state', '$log', '$window', function (rpjYoutube, $scope, $state, $log, $window) {
    $scope.search = function () {
      if (!(rpjYoutube.isEmptyQuery($scope.query)))
        $state.go('search', {q: $scope.query});
    }
  }])
;

