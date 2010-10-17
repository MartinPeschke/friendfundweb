
standardStreamPublish = function(){
 FB.ui(
   {
     method: 'stream.publish',
     message: 'Seeing them all fenced in!',
     attachment: {
       name: 'Connect',
       caption: 'The Facebook Connect JavaScript SDK',
       description: (
         'A small JavaScript library that allows you to harness ' +
         'the power of Facebook, bringing the user\'s identity, ' +
         'social graph and distribution power to your site.'
       ),
       href: 'http://github.com/facebook/connect-js'
     },
     action_links: [
       { text: 'Code', href: 'http://github.com/facebook/connect-js' }
     ],
     user_message_prompt: 'Share your thoughts about Connect'
   },
   function(response) {
     if (response && response.post_id) {
       alert('Post was published.');
     } else {
       alert('Post was not published.');
     }
   }
 );
}