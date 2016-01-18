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
player.controller('PlaybackCtrl', ['$http', '$scope', '$interval', 'playerService', function ($http, $scope, $interval, playerService) {

    /* register watcher for service state */

    $scope.isPlaying = false;
    $scope.volume = 100;
    $scope.position = 0;
    $scope.nowPlaying = {};
    $scope.duration = 100;
    $scope.seekbarOptions = {
        start: [0],
        range: {min: 0, max: $scope.duration}
    };
    $scope.volumeControlOptions = {
        start: [100],
        range: {min: 0, max: 100}
    };

    var incrementSeekbar = function () {
        $scope.seekbarOptions.start[0]++;
        $scope.position += seekbarAutoincrement.stepsize;
    };
    var seekbarAutoincrement = {
        stepsize: 0.5, //in seconds
        incrementer: incrementSeekbar,
        start: function () {
            this.stop();  //cancel previous one
            this._autoincr = $interval(this.incrementer, 1000 * this.stepsize)
        },
        stop: function () {
            $interval.cancel(this._autoincr);
        },
        _autoincr: {}
    };
    var updateState = function (state) {
        //update play state
        $scope.isPlaying = state.isPlaying;
        $scope.nowPlaying = state.nowPlaying;

        /*update seekbar options*/
        //start auto-increment if required
        $scope.isPlaying ? seekbarAutoincrement.start() : seekbarAutoincrement.stop();
        // synchronise position with server
        $scope.seekbarOptions.start = [$scope.position];


        if (!isNaN(state.nowPlaying.duration)) {
            $scope.seekbarOptions.range = {min: 0, max: state.nowPlaying.duration / seekbarAutoincrement.stepsize};
        }
        $scope.position = (state.position == null) ? 0 : state.position / seekbarAutoincrement.stepsize;
        // synchronise position with server
        $scope.seekbarOptions.start = [$scope.position];

        if ($scope.volume != state.volume) {
            $scope.volume = state.volume;
            $scope.volumeControlOptions.start = [state.volume];
        }


    };

    $scope.pauseResume = function () {
        return $http.get('pause').then(function (resp) {
            //updateState(resp.data); //not needed, event handler takes care of the rest
             resp.data.isPlaying ? seekbarAutoincrement.start() : seekbarAutoincrement.stop();

        });
    };
    $scope.rewind = function () {
        return $http.get('rewind');
    };
    $scope.forward = function () {

    };

    playerService.eventSource.addEventListener('stateChanged', function (response) {
        console.log('state change event');
        updateState(JSON.parse(response.data));
        $scope.$apply();
    });

    $http.get('json_state').then(function (response) {
        updateState(response.data)
    });
}]);

player.controller('QueueCtrl', ['$scope', 'playerService', '$http', function ($scope, playerService, $http) {
    $scope.nowPlaying = {}
    $scope.queue = [];
    $scope.$watch(
        function () {
            return playerService.state;
        },
        function (newState) {
            $scope.nowPlaying = newState.nowPlaying;
        },
        false);

    $scope.$watch(
        function () {
            return playerService.queue;
        },
        function (newQueue) {
            if (!queuesEqual($scope.queue, newQueue))
                $scope.queue = newQueue;
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

    /*playerService.getState().then(function(state) {
     $scope.nowPlaying = state.nowPlaying;
     })*/
    playerService.getQueue().then(function (queue) {
        $scope.queue = queue;
    })
}]);

search.controller('searchCtrl', ['rpjYoutube', 'playerService', '$scope', '$stateParams', function (rpjYoutube, playerService, $scope, $stateParams) {
        $scope.loading = false;
        $scope.result = {};
        $scope.result.items = [];

        $scope.ytError = {state: false, message: ""};
        var retries = 0;

        $scope.search = function (query) {
            $scope.loading = true; // set loading to true. First search to complete will set that to false;
            console.log('Searching');

            // youtube search
            ytSearch(query);
            localSearch(query);

        };
        $scope.resultsEmpty = function () {
            return ($scope.result.items == null || !$scope.result.items.length);
        };

        $scope.enqueue = function (song) {
            playerService.addToQueue(song.id);
        };

        $scope.playImmediately = function (song) {
            playerService.play(song.id);
        };

        var ytSearch = function (query) {
            if (rpjYoutube.ready()) {
                rpjYoutube.search(query).then(function (result) {
                    $scope.result = result;
                    $scope.loading = false;
                    console.log('Search finished');
                    console.log($scope.result);
                    $scope.$apply(); //lags if apply is not called
                });
            }
            else if (retries++ < 3) {
                setTimeout(function () {
                    ytSearch(query)
                }, 1000);
            }
            else {
                $scope.ytError = {state: true, message: "Unable to connect to Youtube."}
            }
        };

        var localSearch = function () {
            // TODO: LOCAL search
        };

        //State enter behaviour
        $scope.query = $stateParams.q;
        var query = $stateParams;
        if (rpjYoutube.isEmptyObject(query)) {
            $scope.query = rpjYoutube.lastQuery.q;
            $scope.result = rpjYoutube.lastResult;
            $scope.loading = false;
        }
        else if (!rpjYoutube.ready()) {
            console.log(query);
            $scope.loading = true;
            //wait for gapi to be ready!
            setTimeout(function () {
                $scope.search($stateParams);
            }, 1000);
        }
        else {
            console.log('searching: ' + $stateParams);
            $scope.search($stateParams);
        }
    }])
    .
    controller('searchBarCtrl', ['rpjYoutube', '$scope', '$state', '$log', '$window', function (rpjYoutube, $scope, $state, $log, $window) {
        $scope.search = function () {
            if (!(rpjYoutube.isEmptyObject($scope.query)))
                $state.go('search', {q: $scope.query});
        }
    }])
;

