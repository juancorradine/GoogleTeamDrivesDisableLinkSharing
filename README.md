<h1>Google Team Drives - Disable Link Sharing Script</h1>

Written by: Juan Corradine<br>
Latest revision: 3/Feb/2018

Python script that disables Link Sharing for all files in all Google Team Drives (G Suite) in an organization.

Answer to my own [Stackoverflow question](https://stackoverflow.com/questions/48601854/how-do-i-disable-link-sharing-for-all-files-currently-in-a-team-drive).

We recently migrated thousand of files into several Google Team Drives, and the option "Link Sharing enabled for anyone at the [organization]" was turned on in the Google Apps Admin Console (Apps > G Suite > Drive and Docs > Sharing settings > Link Sharing Defaults: On - Anyone at [Organization]) when we initially moved the files.

We later realized that any user within the organization could search in Google Drive any file in any Team Drive, even if the user didn't have access to that Team Drive (!).

Even after changing this default setting to Off, all the files that were already uploaded kept the link sharing option enabled - Not good!

I found the same question in [Google forum post](https://productforums.google.com/forum/#!msg/apps/sQpsXHxBHsA/Czc5WqSPAgAJ), but it didn't have an answer and also the topic was locked.

So I ended up writing a Python script that uses the [Google Drive API v3](https://developers.google.com/drive/v3/reference/) to go over all the Team Drive files, and remove this Link Sharing option. The script is not very efficient, but it does the job. I recommend running it from a virtual machine in the Google cloud so that it runs faster.

A few things to keep in mind:
* The computer running the script needs to have Python 3.6.X installed (3.6.4 as of this writing), and also the google-api-python-client python package: `pip install --upgrade google-api-python-client`
* You'll also need to turn on the Google Drive API, and create the necessary credentials for the script to work. Just follow the instructions in the Google Drive API v3 [Python Quickstart Guide](https://developers.google.com/drive/v3/web/quickstart/python).
* The API has a default quota limit of 1,000 requests/100 Seconds, so when this limit is reached, the script waits 101 seconds before continuing.
* The script will remove the Link sharing option for either the organization or anyone. So if any user intentionally has a file shared to "Anyone with the Link", this will also be lost.

Hope this helps!
