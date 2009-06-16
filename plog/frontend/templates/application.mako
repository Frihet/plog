<%namespace name="phew" module="phew.template"/>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<head>
  <meta http-equiv="Content-type" content="text/html; charset=utf-8"/>
  <title>${title}</title>
  ${phew.phew_head_links()}
  ${phew.tag_static_css('plog.css')}
  ${phew.tag_static_js('plog.js')}

  <script type="text/javascript">
    $(document).ready(function() {
      ${self.jquery_code()}
    });
  </script>
</head>
<body>
<div id="header">
  ${phew.tag_static_img('plog.png')}

  <ul id="menu">
% for controller, name in (('index', 'Search logs'), ('reports', 'Reports'), ('rules', 'Rules'), ('admin', 'Administration')):
    <li><a href="${container.construct_url(request, controller, 'index')}"
% if controller == request.request_info['controller']:
  class="current"
% endif
         >${name}</a></li>
% endfor
  </ul>
</div>

<div id="body">
  ${self.body()}
</div>

</body>
</html>

<%def name="jquery_code()"></%def>
