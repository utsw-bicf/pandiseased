'use strict';

// IE11 polyfill
if (window && !window.Promise) {
	window.Promise = require('bluebird');
}

//IE11 polyfill (https://gist.github.com/bob-lee/e7520bfcdac266e5490f40c2759cc955)
if ('NodeList' in window && !NodeList.prototype.forEach) {
    console.info('polyfill for IE11');
    NodeList.prototype.forEach = function (callback, thisArg) {
    	thisArg = thisArg || window;
    	for (var i = 0; i < this.length; i++) {
            callback.call(thisArg, this[i], i, this);
        }
    };
}

// Read and clear stats cookie
var cookie = require('js-cookie');
window.stats_cookie = cookie.get('X-Stats') || '';
cookie.set('X-Stats', '', {path: '/', expires: new Date(0)});

// Use a separate tracker for dev / test
var ga = require('google-analytics');
var trackers = {'www.encodeproject.org': 'UA-47809317-1'};
var tracker = trackers[document.location.hostname] || 'UA-47809317-2';
ga('create', tracker, {'cookieDomain': 'none', 'siteSpeedSampleRate': 100});
ga('send', 'pageview');

// Need to know if onload event has fired for safe history api usage.
window.onload = function () {
    window._onload_event_fired = true;
};

var $script = require('scriptjs');
$script.path('/static/build/');

// Load the rest of the app as a separate chunk.
require.ensure(['./libs/compat', './browser'], function(require) {
	require('./libs/compat');  // Shims first
	require('./browser');
}, 'bundle');
