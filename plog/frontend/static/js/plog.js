// Return true if dynamic updating of the page is active
function plog_do_update() {
  return $('[name=search-refresh]').attr('checked');
}

// Fetch logs and insert render html in DOM.
function plog_ajax_logs() {
  $('#logs').load(url_ajax);
}

// Function called to first poll server and check when logs for the
// current filter was last modified, and if never than the current logs
// update the view.
function plog_update_logs() {
  $.getJSON(url_json,
    function (result) {
      if (plog_do_update() && result.last_id > last_id) {
        // New data provided, update last updated values and insert
        // into the current document.
        last_id = result.last_id;
        last_modified = result.last_modified;
        url_json = url_json.replace(/last_id=[0-9]+/, 'last_id=' + last_id);

        plog_insert_logs(result);
        plog_truncate_logs();
        plog_apply_callbacks();
      }

      // Schedule update of logs
      if (plog_do_update()) {
        window.setTimeout(plog_update_logs, update_interval);
      }
    }
  );
}

// Insert log entries, first adding both separate log entries and bulk
// data provided. (Currently no bulk data is added)
function plog_insert_logs(result) {
  // Insert separate entries before the bulk data, they have older
  // mtime than the current element.
  var entry_start = $('#logs_start');

  $.each(result.log_entries, function(i, item){
    var entry = entry_start.next();
    while (entry.length && entry.data('log_time') > item.log_time) {
      entry = entry.next();
    }

    var j_item = jQuery(item.html);
    j_item.data('log_time', item.log_time);

    entry.before(j_item);
  });

  // After separet entires have been added, add the bulk of log
  // entries that have timestamp > last_modified.
  // $('#logs_start').after(result.log_entries_bulk);
}

// Limit amount of log data entries being displayed
function plog_truncate_logs() {
  $('#logs div:gt(' + (max_logs + 1) + ')').remove();
}

// Apply callbacks on new log entries
function plog_apply_callbacks() {
  $('.log_entry').click(function(){
    var extra_id = '#' + $(this).attr('id') + '_extra';
    $(extra_id).toggle();
  });
}
