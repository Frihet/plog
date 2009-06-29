<%!
import simplejson
%>
<%namespace file="plog.mako" import="*"/>
<%namespace name="plog" module="plog.frontend.template"/>
{
  'last_id': ${last_id},
  'last_modified': ${last_modified},
  'log_entries': [
% for log in logs:
    {'log_time': ${log['log_time_unix']},
     'log_type_id': ${log['log_type_id']},
     'html': ${plog.format_log(log) | simplejson.dumps}},
% endfor
  ]
}
