
// Function called to first poll server and check when logs for the
// current filter was last modified, and if never than the current logs
// update the view.
function plog_update_logs() {
  $.getJSON(url,
    function (result) {
      do_update = $('[name=search-refresh]').attr('checked');

      if (result.last_modified > last_modified) {
        last_modified = result.last_modified;

        // New data is available, re-fetch the log area and when completed
        // schedule a recheck.
        $('#logs').load(url_load, {},
          function () {
            if (do_update) {
              window.setTimeout(plog_update_logs, 3000);
            }
          });
      } else if (do_update) {
        window.setTimeout(plog_update_logs, 3000);
      }
    }
  );
}
