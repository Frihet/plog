# This file is part of plog.
#
# plog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# plog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with plog.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Plog frontent template helpers, used for rendering instead of .mako
files as it makes use not writing to buffers easier.
"""

import plog

def format_log_header(context, log):
    """
    Format log header.
    """
    return ''

def _format_log_level(log):
    if log['priority'] < 4:
        return 'log_error'
    elif log['priority'] < 5:
        return 'log_warning'
    else:
        return 'log_info'

def format_log(context, log):
    """
    Format log entry, return string ignoring the context.
    """
    if log['log_type_id'] == plog.LOG_ENTRY_PLAIN:
        return _format_log_plain(log)
    elif log['log_type_id'] == plog.LOG_ENTRY_APPSERVER:
        return _format_log_appserver(log)
    elif log['log_type_id'] == plog.LOG_ENTRY_REQUEST:
        return _format_log_request(log)
    else:
        raise ValueError('unsupported log type %d' % (log['log_type_id'], ))

def _format_log_plain(log):
    """
    Format plain log requests.
    """
    return """<div class="%s log_entry" id="log%d">
  <span>%s</span>
  <span>%s</span>
  <span>%s</span>
</div>""" % (_format_log_level(log), log['id'], log['log_time'],
             log['host_name'], log['msg'])

def _format_log_appserver(log):
    """
    Format appserver log data.
    """
    main =  """<div class="%s log_entry log_appserver" id="log%d">
  <span>%s</span>
  <span>%s</span>
  <span>%s</span>
  <span>%s</span>
</div>""" % (_format_log_level(log), log['id'],
             log['log_time'], log['host_name'],
             log['log_source_name'], log['msg'])

    if log['msg_extra'] and log['msg_extra'] != 'None':
        extra = """<div style="display: none;" id="log%d_extra">
  <pre>%s</pre>
</div>""" % (log['id'], log['msg_extra'])
    else:
        extra = ''

    return ''.join((main, extra))

def _format_log_request(log):
    """
    Format request data, such as apache request logs.
    """
    main = """<div class="%s log_entry log_request" id="log%d">
  <span>%d</span>
  <span>%s</span>
  <span>%s</span>
  <span>%s</span>
  <span>%s</span>
  <span>%s</span>
  <span>%d</span>
  <span>%d</span>
  <span>%dms</span>
  <span><a href="%s">%s</a></span>
</div""" % (_format_log_level(log), log['id'], log['log_time'],
            log['host_name'], log['log_source_name'],
            log['re_ip'], log['re_user_agent'], log['re_method'],
            log['re_size'], log['re_status'], log['re_ms_time'],
            log['re_uri'], log['re_uri'])

    if log['msg_extra'] and log['msg_extra'] != 'None':
        extra = """<div style="display: none;" id="log%d_extra">
  <pre>%s</pre>
</div>""" % (log['id'], log['msg_extra'])
    else:
        extra = ''

    return ''.join((main, extra))
