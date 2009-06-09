<%namespace file="phew.mako" import="*"/>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<head>
  <meta http-equiv="Content-type" content="text/html; charset=utf-8"/>
  <title>${title}</title>
  ${phew_head_links()}
  ${tag_static_css('plog.css')}
  ${tag_static_js('plog.js')}

  <script type="text/javascript">
    $(document).ready(function() {
      ${self.jquery_code()}
    });
  </script>
</head>
<body>
${tag_static_img('plog.png')}

${self.body()}

</body>
</html>

<%def name="jquery_code()"></%def>
