/**
 * Created by jakub on 13/01/16.
 */
var player = angular.module('player', ['ya.nouislider'])
    .factory('playerService', ['$http', '$log', '$interval', function ($http, $log, $interval) {
        'use strict';
        /*create the player service object*/
        var p = {};
        p.eventSource = new EventSource('/subscribe');
        p.state = {nowPlaying: "", volume: 100, isPlaying: false, position: 0};
        p.queue = [];

        p.getState = function () {
            return $http.get('json_state').then(function (response) {
                //console.log(response.data);
                return response.data;
            });
        };
        p.getQueue = function () {
            return $http.get('json_queue').then(function (response) {
                //console.log(response.data);
                return response.data.queue;
            })
        };
        p.play = function (songId) {
            return $http.get("play", {videoId: songId});
        };
        p.addToQueue = function (songId) {
            return $http.get("queue_add?videoId=" + songId);
        };

        p.removeFromQueue = function (index) {
            $http.get("queue_remove?index=" + index);
        };

        p.eventSource.addEventListener('queueChanged', function (response) {
            p.queue = JSON.parse(response.data);
            console.log('Queue change event');
        });
        return p;
    }]);

var search = angular.module('search', ['YtAPI'])
    .factory('rpjYoutube', ['Youtube', function (Youtube) {
        var rpjYt = {};
        //persistent storage of last fetched result
        rpjYt.lastResult = {};
        rpjYt.lastQuery = {};

        rpjYt.ready = function () {
            return Youtube._gapiLoaded;
        }
        rpjYt.search = function (query) {
            rpjYt.lastQuery = query;
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
            type: 'video',
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
