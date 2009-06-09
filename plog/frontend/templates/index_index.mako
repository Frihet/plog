<%namespace file="phew.mako" import="*"/>
<%inherit file="application.mako"/>

<%def name="jquery_code()">
  ${phew_jquery_datetime()}
</%def>

${tag_form('index', 'index', None, 'POST', dict((('class', 'search_form'), )))}
  ${form_search.input_field('search', True)}
  ${form_search.input_field('host', True)}
  ${form_search.input_field('priority', True)}
  ${form_search.input_field('time_start', True)}
  ${form_search.input_field('time_end', True)}

  ${tag_form_submit('Update filter')}
${tag_form_end()}

<script>
// Initial state for the logs updating, used and overriden in plog_update_logs
do_update=true;
last_modified=0;
url="${url_check}"
url_load="${url_load}"

// Run initial fetch of logs, will schedule updates if requested.
plog_update_logs();
</script>

<div id="logs"></div>
