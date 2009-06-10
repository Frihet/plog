<%def name="plog_log_level(log)">
% if log['priority'] < 4:
log_error
% elif log['priority'] < 5:
log_warning
% else:
log_info
% endif
</%def>

<%def name="plog_header_plain()">
<table>
  <tr>
    <th>time</th>
    <th>host</th>
    <th>message</th>
  </tr>
</%def>

<%def name="plog_log_plain(log)">
<tr class="${plog_log_level(log)}">
  <td>${log['log_time']}</td>
  <td>${log['host_name']}</td>
  <td>${log['msg']}</td>
</tr>
</%def>

<%def name="plog_header_appserver()">
<table>
  <tr>
    <th>time</th>
    <th>host</th>
    <th>source</th>    
    <th>message</th>
  </tr>
</%def>

<%def name="plog_log_appserver(log)">
<tr class="${plog_log_level(log)}">
  <td>${log['log_time']}</td>
  <td>${log['host_name']}</td>
  <td>${log['log_source_name']}</td>
  <td>${log['msg']}</td>
</tr>
</%def>

<%def name="plog_header_request()">
<table>
  <tr>
    <th>time</th>
    <th>host</th>
    <td>source</td>
    <th>client</th>
    <th>user agent</th>
    <th>method</th>
    <th>size</th>
    <th>status</th>
    <th>time</th>
    <th>uri</th>
  </tr>
</%def>

<%def name="plog_log_request(log)">
<tr class="${plog_log_level(log)}">
  <td>${log['log_time']}</td>
  <td>${log['host_name']}</td>
  <td>${log['log_source_name']}</td>
  <td>${log['re_ip']}</td>
  <td>${log['re_user_agent']}</td>
  <td>${log['re_method']}</td>
  <td>${log['re_size']}</td>
  <td>${log['re_status']}</td>
  <td>${log['re_ms_time']}ms</td>
  <td><a href="${log['re_uri']}">${log['re_uri']}</a></td>
</tr>
</%def>
