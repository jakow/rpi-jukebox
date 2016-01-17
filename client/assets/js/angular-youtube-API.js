var apiKey = "AIzaSyB7VRxhOfQRkKt0dmULBOsp1wFIMJLStbA";
function initGAPI() {
    console.log('Initialising gapi');
    window.initGapi();
}


angular.module('YtAPI', [])
    .factory('Youtube', ['$log', '$window', '$q', function ($log, $window, $q) {
        var Yt = {};
        Yt._gapiLoaded = false;
        Yt.init = function (callback) {
            console.log('GAPI loaded');
            gapi.client.load('youtube', 'v3').then(function () {
                gapi.client.setApiKey(apiKey);
                Yt._gapiLoaded = true;
                if (callback) callback();
            });
        };
        Yt.gapiLoaded = function () {
            return Yt._gapiLoaded;
        };

        $window.initGapi = function () {
            Yt.init();
        };
        Yt.search = function (query) {
            return gapi.client.youtube.search.list(query);
        };
        /*Yt.GAPIReady = function () {
         var d = $q.defer();
         if (Yt._gapiLoaded) {
         d.resolve()
         }

         };*/
        return Yt;
    }]).run();
