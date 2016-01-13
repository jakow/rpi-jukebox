/**
 * Created by jakub on 13/01/16.
 */

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
          p.updateState(response); //slows things down a bit
          return response.data;
        });
    };

    p.playPause = function () {
      console.log('Requesting play/pause');
      return $http.get('play_pause');
    };

    p.rewind = function () {
      console.log('Requesting rewind');
      return $http.get('rewind');
    };

    p.addToQueue = function (songId) {
      console.log('Adding to queue');
      return p.request('queue_add?videoId=' + songId);
    };

    p.removeFromQueue = function (index) {
      console.log('Removing from queue');
      return p.request('queue_remove?index=' + index);
    }

    p.forward = function () {
      return p.request('forward');
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
        console.log(response);
        rpjYt.lastResult = rpjYt.transformResult(response.result); // save response to be used later
        return rpjYt.lastResult;
      });
    };

    //helper function to determine if no results found
    rpjYt.isEmptyObject = function (query) {
      for (var key in query) {
        if (query.hasOwnProperty(key) && query[key] !== undefined)
          return false;
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

    /*
      transforms the search result so that the object structure is consistent in the frontend and backend.
      ie each queue item consists at least of following:
      - title
      - id
      - uploader
      - thumbnail
     */
    rpjYt.transformResult = function (result) {
      var r = {};
      if (result.nextPageToken) r.nextPageToken = result.nextPageToken;
      if (result.prevPageToken) r.prevPageToken = result.prevPageToken;
      r.items = [];
      var items = result.items;
      for (var i = 0; i < items.length - 1; ++i) {
        r.items.push({
          title: items[i].snippet.title,
          id: items[i].id.videoId,
          thumbnail: items[i].snippet.thumbnails.medium.url,
          uploader: items[i].snippet.channelTitle,
          description: items[i].snippet.description
        });
      }
      return r;
    };
    return rpjYt;
  }])
  ;
