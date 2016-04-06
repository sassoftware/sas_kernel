/*
 *  // Theme selector
 *  // Select your favorite code coloring
 *  // Author:     Jared Dean SAS Instititue
 */

define(["require"], function(require) {
    "use strict";

    var themes = {
        Default: "./themes/theme_default.css",
        _3024_Dark : "./themes/base16-3024-dark.css",
        _3024_Light : "./themes/base16-3024-light.css",
        Ocean_Light : "./themes/base16-ocean-light.css",
        Paraiso_Dark : "./themes/base16-paraiso-dark.css",
        Paraiso_Light : "./themes/base16-paraiso-light.css",
        Pop_Dark : "./themes/base16-pop-dark.css",
        Pop_Light : "./themes/base16-pop-light.css",
        Railscasts_Dark : "./themes/base16-railscasts-dark.css",
        Railscasts_Light : "./themes/base16-railscasts-light.css",
        Shapeshifter_Dark : "./themes/base16-shapeshifter-dark.css",
        Shapeshifter_Light : "./themes/base16-shapeshifter-light.css",
        Solarized_Dark : "./themes/base16-solarized-dark.css",
        Solarized_Light : "./themes/base16-solarized-light.css",
        Summerfruit_Dark : "./themes/base16-summerfruit-dark.css",
        Summerfruit_Light : "./themes/base16-summerfruit-light.css",
        Tomorrow_Dark : "./themes/base16-tomorrow-dark.css",
        Tomorrow_Light : "./themes/base16-tomorrow-light.css",
        Twilight_Dark : "./themes/base16-twilight-dark.css",
        Twilight_Light : "./themes/base16-twilight-light.css",
        SAS_Light : "./themes/base16-sas-light.css"
    };


    function add_to_toolbar(current_theme) {

        var ipython_toolbar = $(IPython.toolbar.element),
        	label = $('<span/>').addClass("navbar-text permissions-list").text('Theme:'),
        	select = $('<select/>').attr('id', 'permissions-select').attr('class', 'permissions-list form-control select-xs');

        // Add label to the toolbar
        ipython_toolbar.append(label).append(select);

        // Add themes to the selector
        for (var key in themes){
            select.append($('<option/>').attr('value', key).text(key));
        }

        // If actually a theme, select it
        if (current_theme){
            select.val(current_theme);
        }

        // Add an action when value is changed
        select.change( function(){
            theme_toggle($(this).val());
        });

    }

    function load_css(theme) {

        // Create a link element to attach the styles
        var link = document.createElement("link");
        link.type = "text/css";
        link.rel = "stylesheet";
        link.href = require.toUrl(themes[theme]);
        link.id = theme + "-css";
        document.getElementsByTagName("head")[0].appendChild(link);
    }

    function unload_css(theme) {

        // Select the theme to unload and remove the link node
        var css = document.getElementById(theme + "-css");
        css.parentNode.removeChild(css);
    }


    function theme_toggle(new_theme) {
    	
        var current_theme = window.localStorage.getItem('nb-theme');

        // Check if there is a theme actually loaded
        if (current_theme) {
            unload_css(current_theme);
        }

		load_css(new_theme);
        window.localStorage.setItem('nb-theme', new_theme);
    }

    function load_theme_selector() {
        
        var current_theme = window.localStorage.getItem('nb-theme');

        add_to_toolbar(current_theme);

        if (current_theme) {
            load_css(current_theme);
        }
                
    }

    return {
        load_ipython_extension: load_theme_selector
    };

});
