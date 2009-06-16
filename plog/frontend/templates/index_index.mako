<%namespace name="phew" module="phew.template"/>
<%inherit file="application.mako"/>

<%def name="jquery_code()">
  ${phew.phew_jquery_datetime()}

  $('[name=search-refresh]').click(function () {
    if ($(this).attr('checked')) {
      plog_update_logs();
    }
  });
</%def>

${phew.tag_form('index', 'index', None, 'POST', dict((('class', 'search_form'), )))}
  ${form_search.input_field('search', True, dict((('class', 'search_field'), )))}<br />
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
last_modified=0;
url="${url_check}"
url_load="${url_load}"

// Run initial fetch of logs, will schedule updates if requested.
plog_update_logs();
</script>

<div id="logs"></div>
