(function() {
	function confirmDeleteLinks() {
		var links = document.querySelectorAll('a.btn.btn-sm.btn-danger');
		links.forEach(function(link) {
			link.addEventListener('click', function(e) {
				// For list page, these go to a confirmation page; allow.
			});
		});
	}

	document.addEventListener('DOMContentLoaded', function() {
		confirmDeleteLinks();
	});
})();


