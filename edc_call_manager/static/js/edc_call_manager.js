function updateAppointment() {
	initial_value = $('#id_appt').find('option[selected]').val()
	$('#id_appt').val(initial_value);
  if (initial_value == 'Yes') {
    showAppointment();
  } else {
  	hideAppointment();
	hideOtherLocation();  	
  };
  $('#id_appt').change( function(e) {
    if (this.value == 'Yes') {
    	showAppointment();
    } else {
    	hideAppointment();
    	hideOtherLocation();    	
    }        
  });

}

function updateOtherLocation() {
	initial_value = $('#id_appt_location').find('option[selected]').val()
	$('#id_appt_location').val(initial_value);
  if ( initial_value == 'OTHER') {
  	showOtherLocation();
  } else {
	hideOtherLocation();
  };
  $('#id_appt_location').change( function(e) {
    if (this.value == 'OTHER') {
	  	showOtherLocation();
    } else {
    	hideOtherLocation();
    }        
  });
}

function updateContacted() {
	initial_value = $('#id_contact_type').find('option[selected]').val();
   	$('#id_contact_type').val(initial_value);
  if (initial_value == 'direct') {
    showDirectContact();
  } else if (initial_value == 'indirect') {
    showIndirectContact();
	hideAppointment();
	hideOtherLocation();
  } else {
  	hideContact();
	hideAppointment();
	hideOtherLocation();
  };
  $('#id_contact_type').change( function(e) {
    if (this.value == 'direct') {
    	showDirectContact();
    } else if (this.value == 'indirect') {
    	showIndirectContact();
    	hideAppointment();
		hideOtherLocation();
    } else {
  		hideContact();
    	hideAppointment();
		hideOtherLocation();
    }
  });
}

function showDirectContact() {
    $('#div_id_appt').show();
    $('#div_id_may_call').show();
    $('#id_appt').prop( "required", true );
    $('#id_may_call').prop( "required", true ).val('Yes');
    $('#div_id_time_of_week').hide();
    $('#div_id_time_of_day').hide();
    $('#id_time_of_week').prop( "required", false ).val('');
    $('#id_time_of_day').prop( "required", false ).val('');
}

function showIndirectContact() {
    $('#div_id_time_of_week').show();
    $('#div_id_time_of_day').show();
    $('#div_id_may_call').show();
    $('#id_time_of_week').prop( "required", true );
    $('#id_time_of_day').prop( "required", true );
    $('#id_may_call').prop( "required", true ).val('Yes');
    $('#div_id_appt').hide();
    $('#id_appt').prop( "required", false ).val('');
}

function hideContact() {
    $('#div_id_time_of_week').hide();
    $('#div_id_time_of_day').hide();
    $('#div_id_appt').hide();
    $('#div_id_may_call').hide();
    $('#id_appt').prop( "required", false ).val('');
    $('#id_time_of_week').prop( "required", false ).val('');
    $('#id_time_of_day').prop( "required", false ).val('');
    $('#id_may_call').prop( "required", false ).val('');	
}

function showAppointment() {
    $('#div_id_appt_date').show();
    $('#div_id_appt_grading').show();  
    $('#div_id_appt_location').show();
    $('#id_appt_date').prop( "required", true );
    $('#id_appt_grading').prop( "required", true );  
    $('#id_appt_location').prop( "required", true );
    $('#id_appt_other_location').prop( "required", false ).val('');	
}

function hideAppointment() {
    $('#div_id_appt_date').hide();  
    $('#div_id_appt_grading').hide();  
    $('#div_id_appt_location').hide();
    $('#div_id_appt_location_other').hide();
    $('#id_appt_date').prop( "required", false ).val('');
    $('#id_appt_grading').prop( "required", false ).val('');  
    $('#id_appt_location').prop( "required", false ).val('');	
    $('#id_appt_other_location').prop( "required", false ).val('');	
}

function showOtherLocation() {
    $('#div_id_appt_location_other').show();
    $('#id_appt_location_other').prop( "required", true );  
}

function hideOtherLocation() {
    $('#div_id_appt_location_other').hide();
    $('#id_appt_location_other').prop( "required", false ).val('');  
}