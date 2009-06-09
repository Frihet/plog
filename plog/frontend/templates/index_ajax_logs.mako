<%namespace file="plog.mako" import="*"/>

<% type_id = -1 %>

% for log in logs:
  % if log['log_type'] != type_id:
    <% type_id = log['log_type'] %>

    % if type_id == 1:
      ${plog_header_request()}
    % elif type_id == 2:
      ${plog_header_appserver()}
    % else:
      ${plog_header_plain()}
    % endif
  % endif

  % if log['log_type'] == 1:
    ${plog_log_request(log)}
  % elif log['log_type'] == 2:
    ${plog_log_appserver(log)}
  % else:
    ${plog_log_plain(log)}
  % endif
% endfor
</table>
