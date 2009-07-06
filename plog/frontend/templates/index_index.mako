<%namespace name="phew" module="phew.template"/>
<%inherit file="application.mako"/>

<%def name="jquery_code()">
  ${phew.phew_jquery_datetime()}

  // Run initial fetch of logs, will schedule updates if requested.
  if (plog_do_update()) {
    plog_update_logs();
  } else {
    plog_ajax_logs();
  }

  $('[name=search-refresh]').click(function () {
    if ($(this).attr('checked')) {
      $('.phew_pagination').remove();
      plog_update_logs();
    } else {
      // FIXME: Preserve current position
      plog_ajax_logs();
    }
  });
</%def>

${phew.tag_form('index', 'index', None, 'POST', dict((('class', 'search_form'), )))}
  ${form_search.input_field('search', True, dict((('class', 'search_field'), )))}<br />
  ${form_search.input_field('environment', True)}
  ${form_search.input_field('host', True)}
  ${form_search.input_field('source', True)}
  ${form_search.input_field('priority', True)}
  ${form_search.input_field('time_start', True)}
  ${form_search.input_field('time_end', True)}
  ${phew.tag_form_submit('Update filter')}
  ${form_search.input_field('refresh', True)}
${phew.tag_form_end()}

<script type="text/javascript">
// Initial state for the logs updating, used and overriden in plog_update_logs
last_id=0
last_modified=0;
<%doc>
FIXME: Start using user settings (falling back to system defaults) instead of
       hardcoded values.
</%doc>
max_logs=5000;
url_json="${url_json}"
url_ajax="${url_ajax}"
update_interval=2000;
</script>

<div id="logs">
  <div id="logs_start"></div>
  <div id="logs_end"></div>
</div>
