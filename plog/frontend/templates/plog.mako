<%def name="plog_header_plain()">
<table cellspacing="0">
  <tr>
    <th>time</th>
    <th>host</th>
    <th>message</th>
  </tr>
</%def>

<%def name="plog_header_appserver()">
<table cellspacing="0">
  <tr>
    <th>time</th>
    <th>host</th>
    <th>source</th>    
    <th>message</th>
  </tr>
</%def>

<%def name="plog_header_request()">
<table cellspacing="0">
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

