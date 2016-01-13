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
      $scope.playing = response.isPlaying;
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
      return playerService.state;
    },
    function (newState) {
      $scope.nowPlaying = newState.nowPlaying;
      // if (!queuesEqual($scope.queue, newState.queue))
      $scope.queue = newState.queue;
    },
    false);

  $scope.remove = function (index) {
    //first remove from real queue
    playerService.removeFromQueue(index);
    //then remove from view
    $scope.queue.splice(index, 1);
  };

  function queuesEqual(a, b) {
  if (a === b) return true;
  if (a == null || b == null) return false;
  if (a.length != b.length) return false;

  for (var i = 0; i < a.length; ++i) {
    if (a[i].id !== b[i].id) return false;
  }
  return true;
}

}]);

search.controller('searchCtrl', ['rpjYoutube', 'playerService', '$scope', '$stateParams', '$window', function (rpjYoutube, playerService, $scope, $stateParams, $window) {
    $scope.loading = false;
    $scope.result = {};
    $scope.result.items = [];

    $scope.search = function (query) {
      $scope.loading = true;
      console.log('Searching')
      rpjYoutube.search(query).then(function (result) {
        $scope.result = result;
        $scope.loading = false;
        console.log('Search finished');
        console.log($scope.result);
        $scope.$apply(); //lags if apply is not called
      });
    };
    $scope.resultsEmpty = function () {
      if ($scope.result.items == null ) return true;
      if (!$scope.result.items.length) return true;
      else return false;
    };

    $scope.enqueue = function (song) {
      playerService.addToQueue(song.id);
      playerService.state.queue.push(song);
    };

    //State enter behaviour
    $scope.query = $stateParams.q;
    var query = $stateParams;
    if (rpjYoutube.isEmptyObject(query)) {
      $scope.query = rpjYoutube.lastQuery.q;
      $scope.result = rpjYoutube.lastResult;
    }
    else if (!rpjYoutube.ready()) {
      console.log(query);
      $scope.loading = true;
      //wait for gapi to be ready!
      setTimeout(function () { $scope.search($stateParams)  }, 1000);
    }
    else {
      console.log('searching: ' + $stateParams);
      $scope.search($stateParams);
    }

  }])
  .controller('searchBarCtrl', ['rpjYoutube', '$scope', '$state', '$log', '$window', function (rpjYoutube, $scope, $state, $log, $window) {
    $scope.search = function () {
      if (!(rpjYoutube.isEmptyObject($scope.query)))
        $state.go('search', {q: $scope.query});
    }
  }])
;

