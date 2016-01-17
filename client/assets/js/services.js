/**
 * Created by jakub on 13/01/16.
 */
var player = angular.module('player', ['ya.nouislider'])
    .factory('playerService', ['$http', '$log', '$interval', function ($http, $log, $interval) {
        'use strict';
        /*create the player service object*/
        var p = {};
        p.eventSource = new EventSource('/subscribe');

        /* helpers */
        p.state = {};
        p.queue = [];

        p.getState = function () {
            return $http.get('json_state').then(function (response) {
                console.log(response.data);
                p.state = response.data;
                return response.data;
            });
        };
        p.getQueue = function () {
            return $http.get('json_queue').then(function (response) {
                console.log(response.data);
                p.queue = response.data;
                return response.data;
            })
        };

        p.playPause = function () {

        };

        p.rewind = function () {

        };

        p.forward = function () {

        };

        p.addToQueue = function (songId) {

        };

        p.removeFromQueue = function (index) {
        };

        p.forward = function () {
        };
        //finally when all functions are set up, add event listeners
        p.eventSource.addEventListener('stateChanged', function (response) {
            p.state = response.data;
            console.log(response);
        });
        p.eventSource.addEventListener('queueChanged', function (response) {
            p.queue = response.data;
            console.log(response);
        });
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
