<%namespace name="plog" module="plog.frontend.template"/>

<script type="text/javascript">
  $(document).ready(function() {
    // Enable toggling of elements
    $('.log_entry').click(function () {
      extra_id = '#' + $(this).attr('id') + '_extra';
      $(extra_id).toggle();
    });

    // Enable ajaxy pagination
    $('.phew_pagination > span > a').click(function() {
      url = $(this).attr('href').replace('a=index', 'a=ajax_logs');
      $('#logs').load(url);
      return false;
    });

    // Update last ID from results
    log = $('#logs_start + div');
    if (log.length) {
      last_id = log.attr('id').replace('log', '');
      if (last_id.match(/^[0-9]+$/)) {
        url_json = url_json.replace(/last_id=[0-9]+/, 'last_id=' + last_id);
      }
    }
  });
</script>

${form_search.render_pagination()}

<div id="logs_start"></div>

<% log_type_id = -1 %>

% for log in logs:
  % if log['log_type_id'] != log_type_id:
    <% log_type_id = log['log_type_id'] %>
      ${plog.format_log_header(log)}
  % endif

  ${plog.format_log(log)}
% endfor

<div id="logs_end"></div>

${form_search.render_pagination()}
