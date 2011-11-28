var POLL = (function() {
  var $quoteContainer;

  var writeMessage = function(text) {
    $quoteContainer.fadeOut('slow', function() {
      $quoteContainer.text(text);
      $quoteContainer.fadeIn('slow');
    });
  };

  var poll = function() {
    $.ajax({
      type: 'GET',
      url: '/poll',
      async: true,
      cache: false,
      timeout: 30000,
      success: function(data) {
        writeMessage(data.quote);
      },
      complete: function() {
        poll();
      }
    });
  };

  var buildPollBox = function(config) {
    $quoteContainer = $(config.quoteContainer);
    poll();
  };

  return {
    buildPollBox: buildPollBox
  }
})();
